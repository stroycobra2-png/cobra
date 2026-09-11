import json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,QWidget,QFrame,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QPushButton,
    QStackedWidget,QScrollArea,QProgressBar,QMessageBox,QDialog,QLineEdit,QSpinBox,
    QComboBox,QRadioButton,QButtonGroup,QTextEdit,QTableWidget,QTableWidgetItem,QHeaderView,
    QCheckBox
)
from .curriculum import PLACEMENT_QUESTIONS, LEVELS
from .database import LEVEL_ORDER, SKILLS
from .services import SpeechService, speaking_score, writing_score
from .styles import get_stylesheet


def clear_layout(layout):
    while layout.count():
        item=layout.takeAt(0)
        w=item.widget()
        if w: w.deleteLater()
        elif item.layout(): clear_layout(item.layout())


def make_label(text, obj=None, wrap=False):
    l=QLabel(text)
    if obj: l.setObjectName(obj)
    l.setWordWrap(wrap)
    return l


def card(title=None):
    f=QFrame(); f.setObjectName('card'); lay=QVBoxLayout(f); lay.setContentsMargins(20,18,20,18)
    if title: lay.addWidget(make_label(title,'cardTitle'))
    return f,lay


def button(text, primary=True):
    b=QPushButton(text); b.setObjectName('primaryButton' if primary else 'secondaryButton'); b.setCursor(Qt.PointingHandCursor); return b


class SetupDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self.setWindowTitle('FluentPath — İlk Kurulum'); self.setModal(True); self.setMinimumWidth(520)
        lay=QVBoxLayout(self); lay.setContentsMargins(28,28,28,28); lay.setSpacing(14)
        lay.addWidget(make_label('FluentPath’e Hoş Geldin','pageTitle'))
        lay.addWidget(make_label('A1’den C2’ye kadar kişisel İngilizce yolculuğunu başlat.','muted',True))
        lay.addWidget(QLabel('Adın'))
        self.name=QLineEdit(); self.name.setPlaceholderText('Öğrenci'); lay.addWidget(self.name)
        lay.addWidget(QLabel('Günlük hedef (dakika)'))
        self.goal=QSpinBox(); self.goal.setRange(5,180); self.goal.setValue(20); lay.addWidget(self.goal)
        start=button('A1’den sıfırdan başla'); start.clicked.connect(self.start_a1); lay.addWidget(start)
        placement=button('Seviye tespit sınavına gir',False); placement.clicked.connect(self.start_placement); lay.addWidget(placement)
    def start_a1(self):
        self.db.set_setup(self.name.text(), 'A1', self.goal.value()); self.accept()
    def start_placement(self):
        dlg=PlacementDialog(self.db,self.name.text(),self.goal.value(),self)
        if dlg.exec()==QDialog.Accepted: self.accept()


class PlacementDialog(QDialog):
    def __init__(self, db, name, goal, parent=None):
        super().__init__(parent); self.db=db; self.name=name; self.goal=goal; self.index=0; self.correct=0
        self.setWindowTitle('Seviye Tespit Sınavı'); self.setMinimumSize(650,430)
        lay=QVBoxLayout(self); lay.setContentsMargins(26,26,26,26)
        self.progress=QProgressBar(); self.progress.setRange(0,len(PLACEMENT_QUESTIONS)); lay.addWidget(self.progress)
        self.level_hint=make_label('','accentText'); lay.addWidget(self.level_hint)
        self.q=make_label('','cardTitle',True); lay.addWidget(self.q)
        self.group=QButtonGroup(self); self.radios=[]
        for i in range(4):
            r=QRadioButton(); self.group.addButton(r,i); self.radios.append(r); lay.addWidget(r)
        lay.addStretch(); self.next=button('Cevapla →'); self.next.clicked.connect(self.answer); lay.addWidget(self.next,alignment=Qt.AlignRight)
        self.load()
    def load(self):
        level,q,opts,correct=PLACEMENT_QUESTIONS[self.index]
        self.level_hint.setText(f'Soru {self.index+1}/{len(PLACEMENT_QUESTIONS)} • {level} bölümü')
        self.q.setText(q); self.group.setExclusive(False)
        for r in self.radios: r.setChecked(False)
        self.group.setExclusive(True)
        for r,t in zip(self.radios,opts): r.setText(t)
        self.progress.setValue(self.index)
    def answer(self):
        checked=self.group.checkedId()
        if checked<0: QMessageBox.information(self,'Cevap seç','Bir seçenek seçmelisin.'); return
        if checked==PLACEMENT_QUESTIONS[self.index][3]: self.correct+=1
        self.index+=1
        if self.index>=len(PLACEMENT_QUESTIONS): self.finish(); return
        self.load()
    def finish(self):
        score=round(self.correct/len(PLACEMENT_QUESTIONS)*100)
        if score<28: level='A1'
        elif score<45: level='A2'
        elif score<62: level='B1'
        elif score<76: level='B2'
        elif score<90: level='C1'
        else: level='C2'
        self.db.set_setup(self.name, level, self.goal)
        self.db.save_placement(score, level)
        QMessageBox.information(self,'Sonuç',f'Puanın: %{score}\nTahmini seviyen: {level}\n\nİstersen alt seviyelerdeki dersleri de tekrar edebilirsin.')
        self.accept()


class DashboardPage(QWidget):
    def __init__(self,db,window):
        super().__init__(); self.db=db; self.window=window
        self.root=QVBoxLayout(self); self.root.setContentsMargins(36,30,36,30); self.root.setSpacing(18)
        self.title=make_label('','pageTitle'); self.root.addWidget(self.title)
        self.subtitle=make_label('Bugün kısa ama düzenli çalış. İlerleme otomatik kaydedilir.','muted',True); self.root.addWidget(self.subtitle)
        self.stats_layout=QHBoxLayout(); self.root.addLayout(self.stats_layout)
        self.hero,self.hero_lay=card(); self.hero.setObjectName('heroCard'); self.root.addWidget(self.hero)
        self.skills,self.skills_lay=card('Beceri Durumu'); self.root.addWidget(self.skills)
        self.root.addStretch(); self.refresh()
    def stat(self,title,value,note):
        f,l=card(); l.addWidget(make_label(title,'muted')); l.addWidget(make_label(str(value),'statValue')); l.addWidget(make_label(note,'muted')); return f
    def refresh(self):
        clear_layout(self.stats_layout); clear_layout(self.hero_lay); clear_layout(self.skills_lay)
        p=self.db.get_profile(); s=self.db.stats(); self.title.setText(f"Merhaba, {p['name']} 👋")
        self.stats_layout.addWidget(self.stat('Seviye',p['current_level'],'CEFR'))
        self.stats_layout.addWidget(self.stat('Toplam XP',p['xp'],'öğrenme puanı'))
        self.stats_layout.addWidget(self.stat('🔥 Seri',p['streak'],'gün'))
        self.stats_layout.addWidget(self.stat('Kelime',s['words'],'öğrenme havuzu'))
        self.hero_lay.addWidget(make_label('BUGÜNKÜ HEDEF','accentText'))
        mins=self.db.today_minutes(); goal=p['daily_goal']
        self.hero_lay.addWidget(make_label(f'{mins} / {goal} dakika','cardTitle'))
        bar=QProgressBar(); bar.setRange(0,max(1,goal)); bar.setValue(min(mins,goal)); self.hero_lay.addWidget(bar)
        row=QHBoxLayout(); go=button('Derslere devam et →'); go.clicked.connect(lambda:self.window.open_page('levels')); row.addWidget(go)
        review=button(f"Tekrar ({len(self.db.due_words())})",False); review.clicked.connect(lambda:self.window.open_page('review')); row.addWidget(review); row.addStretch(); self.hero_lay.addLayout(row)
        scores=self.db.skill_scores()
        names={'vocabulary':'Kelime','grammar':'Grammar','reading':'Reading','listening':'Listening','speaking':'Speaking','writing':'Writing'}
        for sk in SKILLS:
            r=QHBoxLayout(); r.addWidget(QLabel(names[sk])); pb=QProgressBar(); pb.setRange(0,100); pb.setValue(scores[sk]); r.addWidget(pb,1); r.addWidget(QLabel(f"%{scores[sk]}")); self.skills_lay.addLayout(r)


class LevelsPage(QWidget):
    def __init__(self,db,window):
        super().__init__(); self.db=db; self.window=window
        outer=QVBoxLayout(self); outer.setContentsMargins(36,30,36,30); outer.addWidget(make_label('Seviye Haritası','pageTitle'))
        self.info=make_label('A1 → C2 yolculuğun. Kilitler ilerledikçe açılır.','muted'); outer.addWidget(self.info)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); self.content=QWidget(); self.list=QVBoxLayout(self.content); scroll.setWidget(self.content); outer.addWidget(scroll)
        self.refresh()
    def refresh(self):
        clear_layout(self.list); p=self.db.get_profile()
        for level in self.db.get_levels():
            lessons=self.db.get_lessons(level['code']); completed=sum(1 for x in lessons if x['completed']); accessible=self.db.level_accessible(level['code'])
            f=QFrame(); f.setObjectName('levelCard'); row=QHBoxLayout(f); row.setContentsMargins(20,16,20,16)
            badge=make_label(level['code'],'levelBadge'); badge.setFixedWidth(62); row.addWidget(badge)
            v=QVBoxLayout(); v.addWidget(make_label(level['title'],'cardTitle')); v.addWidget(make_label(level['description'],'muted',True)); pb=QProgressBar(); pb.setRange(0,max(1,len(lessons))); pb.setValue(completed); v.addWidget(pb); row.addLayout(v,1)
            b=button('Dersleri aç' if accessible else '🔒 Kilitli',accessible); b.setEnabled(accessible)
            if accessible: b.clicked.connect(lambda _,code=level['code']:self.show_lessons(code))
            row.addWidget(b); self.list.addWidget(f)
        self.list.addStretch()
    def show_lessons(self,level):
        clear_layout(self.list); back=button('← Seviyelere dön',False); back.clicked.connect(self.refresh); self.list.addWidget(back,alignment=Qt.AlignLeft)
        self.list.addWidget(make_label(f'{level} Dersleri','pageTitle'))
        for l in self.db.get_lessons(level):
            accessible=self.db.lesson_accessible(l['id']); f,lay=card(); row=QHBoxLayout(); num=make_label('✓' if l['completed'] else str(l['position']),'lessonNumber'); num.setFixedWidth(52); row.addWidget(num)
            v=QVBoxLayout(); v.addWidget(make_label(l['title'],'cardTitle')); v.addWidget(make_label(l['description'],'muted',True));
            if l['best_score']: v.addWidget(make_label(f"En iyi skor: %{l['best_score']}",'accentText'))
            row.addLayout(v,1); b=button('Aç' if accessible else '🔒',accessible); b.setEnabled(accessible)
            if accessible: b.clicked.connect(lambda _,lid=l['id']:self.window.open_lesson(lid))
            row.addWidget(b); lay.addLayout(row); self.list.addWidget(f)
        self.list.addStretch()


class LessonPage(QWidget):
    def __init__(self,db,window,lesson_id):
        super().__init__(); self.db=db; self.window=window; self.lesson=db.get_lesson(lesson_id); self.groups=[]
        outer=QVBoxLayout(self); outer.setContentsMargins(30,24,30,24)
        back=button('← Derslere dön',False); back.clicked.connect(lambda:self.window.open_page('levels')); outer.addWidget(back,alignment=Qt.AlignLeft)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); cont=QWidget(); lay=QVBoxLayout(cont); lay.setSpacing(14); scroll.setWidget(cont); outer.addWidget(scroll)
        l=self.lesson; lay.addWidget(make_label(f"{l['level_code']} • {l['title']}",'pageTitle')); lay.addWidget(make_label(l['description'],'muted'))
        f,fl=card('Grammar'); fl.addWidget(make_label(l['grammar'],'accentText')); fl.addWidget(make_label('Bu yapıyı örnek cümlede gör ve ardından kendi cümlelerini üret.','muted',True)); lay.addWidget(f)
        vf,vl=card('Kelime Kartları')
        for v in json.loads(l['vocabulary']): vl.addWidget(QLabel(f"<b>{v['word']}</b> — {v['translation']}"))
        lay.addWidget(vf)
        ef,el=card('Örnek Cümle'); el.addWidget(make_label(l['example'],'cardTitle',True)); speak=button('🔊 Dinle',False); speak.clicked.connect(lambda:self.window.speak(l['example'])); el.addWidget(speak,alignment=Qt.AlignLeft); lay.addWidget(ef)
        rf,rl=card('Reading'); rl.addWidget(make_label(l['reading_text'],None,True)); lay.addWidget(rf)
        lf,ll=card('Listening'); ll.addWidget(make_label('Metni görmeden önce dinlemeyi dene. Sonra metni kontrol edebilirsin.','muted',True)); listen=button('▶ Listening’i oynat'); listen.clicked.connect(lambda:self.window.speak(l['listening_text'])); ll.addWidget(listen,alignment=Qt.AlignLeft); reveal=make_label(l['listening_text'],'muted',True); reveal.setVisible(False); rv=button('Metni göster',False); rv.clicked.connect(lambda:reveal.setVisible(not reveal.isVisible())); ll.addWidget(rv,alignment=Qt.AlignLeft); ll.addWidget(reveal); lay.addWidget(lf)
        sf,sl=card('Speaking'); sl.addWidget(make_label('Şu cümleyi söyle:','muted')); sl.addWidget(make_label(l['speaking_prompt'],'cardTitle',True)); sp=button('Speaking modülüne git',False); sp.clicked.connect(lambda:self.window.open_page('speaking')); sl.addWidget(sp,alignment=Qt.AlignLeft); lay.addWidget(sf)
        wf,wl=card('Writing'); wl.addWidget(make_label(l['writing_prompt'],None,True)); wp=button('Writing modülüne git',False); wp.clicked.connect(lambda:self.window.open_page('writing')); wl.addWidget(wp,alignment=Qt.AlignLeft); lay.addWidget(wf)
        qf,ql=card('Ders Sonu Quiz'); self.quiz=json.loads(l['quiz'])
        for qi,q in enumerate(self.quiz):
            ql.addWidget(make_label(f"{qi+1}. {q['question']}",'cardTitle',True)); g=QButtonGroup(self); self.groups.append(g)
            for i,opt in enumerate(q['options']): r=QRadioButton(opt); g.addButton(r,i); ql.addWidget(r)
        submit=button('Dersi değerlendir'); submit.clicked.connect(self.submit); ql.addWidget(submit,alignment=Qt.AlignLeft); lay.addWidget(qf); lay.addStretch()
    def submit(self):
        correct=0
        for g,q in zip(self.groups,self.quiz):
            if g.checkedId()<0: QMessageBox.information(self,'Eksik','Tüm soruları cevapla.'); return
            if g.checkedId()==q['correct']: correct+=1
        score=round(correct/len(self.quiz)*100)
        if score>=67:
            xp=self.db.complete_lesson(self.lesson['id'],score); QMessageBox.information(self,'Ders tamamlandı',f'Skor: %{score}\n+{xp} XP\n\nKelime kartları tekrar havuzuna eklendi.'); self.window.open_page('levels')
        else:
            self.db.log_activity('Quiz denemesi','grammar',score,3,3); QMessageBox.warning(self,'Tekrar dene',f'Skor: %{score}. Dersi tamamlamak için en az %67 gerekiyor.')


class VocabularyPage(QWidget):
    def __init__(self,db):
        super().__init__(); self.db=db; lay=QVBoxLayout(self); lay.setContentsMargins(36,30,36,30); lay.addWidget(make_label('Kelime Merkezi','pageTitle')); self.summary=make_label('','muted'); lay.addWidget(self.summary)
        self.table=QTableWidget(0,5); self.table.setHorizontalHeaderLabels(['★','Seviye','Kelime','Türkçe','Sonraki tekrar']); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); lay.addWidget(self.table)
    def refresh(self):
        words=self.db.all_words(); self.summary.setText(f'{len(words)} kelime öğrenme havuzunda. Ders tamamladıkça yeni kelimeler buraya gelir.')
        self.table.setRowCount(len(words))
        for r,w in enumerate(words):
            vals=['★' if w['favorite'] else '☆',w['level_code'],w['word'],w['translation'],w['due_date']]
            for c,v in enumerate(vals): self.table.setItem(r,c,QTableWidgetItem(str(v)))


class ReviewPage(QWidget):
    def __init__(self,db):
        super().__init__(); self.db=db; self.words=[]; self.index=0; lay=QVBoxLayout(self); lay.setContentsMargins(36,30,36,30); lay.addWidget(make_label('Akıllı Tekrar','pageTitle')); self.info=make_label('','muted'); lay.addWidget(self.info)
        self.f,self.fl=card(); lay.addWidget(self.f); lay.addStretch(); self.refresh()
    def refresh(self):
        self.words=list(self.db.due_words()); self.index=0; self.render()
    def render(self):
        clear_layout(self.fl)
        if not self.words or self.index>=len(self.words): self.info.setText('Bugün için bekleyen tekrar kalmadı 🎉'); self.fl.addWidget(make_label('Harika! Bir sonraki tekrar zamanı gelince kelimeler burada görünecek.','cardTitle',True)); return
        w=self.words[self.index]; self.info.setText(f'{self.index+1}/{len(self.words)} tekrar')
        self.fl.addWidget(make_label(w['word'],'pageTitle')); reveal=make_label('Cevabı görmek için butona bas.','muted'); self.fl.addWidget(reveal)
        rb=button('Anlamı göster',False); rb.clicked.connect(lambda:reveal.setText(f"{w['translation']}\n\nÖrnek: {w['example']}")); self.fl.addWidget(rb,alignment=Qt.AlignLeft)
        row=QHBoxLayout()
        for label,q in [('Zor','hard'),('Orta','medium'),('Kolay','easy')]:
            b=button(label,q=='easy'); b.clicked.connect(lambda _,quality=q:self.rate(quality)); row.addWidget(b)
        self.fl.addLayout(row)
    def rate(self,q):
        self.db.review_word(self.words[self.index]['id'],q); self.index+=1; self.render()


class ListeningPage(QWidget):
    def __init__(self,db,window):
        super().__init__(); self.db=db; self.window=window; lay=QVBoxLayout(self); lay.setContentsMargins(36,30,36,30); lay.addWidget(make_label('Listening Lab','pageTitle'))
        self.combo=QComboBox(); lay.addWidget(self.combo); self.text=make_label('','muted',True); self.text.setVisible(False); lay.addWidget(self.text)
        row=QHBoxLayout(); play=button('▶ Dinle'); play.clicked.connect(self.play); row.addWidget(play); show=button('Metni göster/gizle',False); show.clicked.connect(lambda:self.text.setVisible(not self.text.isVisible())); row.addWidget(show); row.addStretch(); lay.addLayout(row)
        self.check=QLineEdit(); self.check.setPlaceholderText('Duyduğun cümleden hatırladığın kısmı İngilizce yaz...'); lay.addWidget(self.check); score=button('Kendini değerlendir',False); score.clicked.connect(self.evaluate); lay.addWidget(score,alignment=Qt.AlignLeft); lay.addStretch(); self.refresh()
    def refresh(self):
        self.combo.clear();
        for level in LEVEL_ORDER:
            if self.db.level_accessible(level):
                for l in self.db.get_lessons(level): self.combo.addItem(f"{level} • {l['title']}",l['id'])
        self.combo.currentIndexChanged.connect(self.load); self.load()
    def load(self):
        if self.combo.currentData(): self.text.setText(self.db.get_lesson(self.combo.currentData())['listening_text'])
    def play(self):
        if not self.combo.currentData(): return
        self.window.speak(self.db.get_lesson(self.combo.currentData())['listening_text'])
    def evaluate(self):
        if not self.combo.currentData(): return
        target=self.db.get_lesson(self.combo.currentData())['listening_text']; score=speaking_score(target,self.check.text()); self.db.log_activity('Listening pratiği','listening',score,8,5); QMessageBox.information(self,'Listening',f'Yakalama puanın: %{score}\nBu puan yazdığın ifadelerin hedef metinle benzerliğine göre hesaplandı.')


class SpeakingPage(QWidget):
    def __init__(self,db,window):
        super().__init__(); self.db=db; self.window=window; lay=QVBoxLayout(self); lay.setContentsMargins(36,30,36,30); lay.addWidget(make_label('Speaking Studio','pageTitle'))
        self.combo=QComboBox(); lay.addWidget(self.combo); self.target=make_label('','cardTitle',True); lay.addWidget(self.target)
        row=QHBoxLayout(); hear=button('🔊 Örneği dinle',False); hear.clicked.connect(lambda:self.window.speak(self.target.text())); row.addWidget(hear); mic=button('🎤 Mikrofondan algıla'); mic.clicked.connect(self.mic); row.addWidget(mic); row.addStretch(); lay.addLayout(row)
        self.input=QLineEdit(); self.input.setPlaceholderText('Mikrofon yoksa söylediğin/çalıştığın cümleyi buraya yaz...'); lay.addWidget(self.input); ev=button('Telaffuz/benzerlik puanını hesapla'); ev.clicked.connect(self.evaluate); lay.addWidget(ev,alignment=Qt.AlignLeft); self.result=make_label('','accentText',True); lay.addWidget(self.result); lay.addStretch(); self.refresh()
    def refresh(self):
        self.combo.clear()
        for level in LEVEL_ORDER:
            if self.db.level_accessible(level):
                for l in self.db.get_lessons(level): self.combo.addItem(f"{level} • {l['title']}",l['id'])
        self.combo.currentIndexChanged.connect(self.load); self.load()
    def load(self):
        if self.combo.currentData(): self.target.setText(self.db.get_lesson(self.combo.currentData())['speaking_prompt'])
    def mic(self):
        ok,text=self.window.speech.listen_once()
        if ok: self.input.setText(text); self.evaluate()
        else: QMessageBox.information(self,'Mikrofon',text)
    def evaluate(self):
        score=speaking_score(self.target.text(),self.input.text()); self.result.setText(f'Benzerlik puanı: %{score}'); self.db.log_activity('Speaking pratiği','speaking',score,10,5)


class WritingPage(QWidget):
    def __init__(self,db):
        super().__init__(); self.db=db; lay=QVBoxLayout(self); lay.setContentsMargins(36,30,36,30); lay.addWidget(make_label('Writing Coach','pageTitle')); self.combo=QComboBox(); lay.addWidget(self.combo); self.prompt=make_label('','cardTitle',True); lay.addWidget(self.prompt); self.editor=QTextEdit(); self.editor.setPlaceholderText('İngilizce metnini yaz...'); lay.addWidget(self.editor,1); b=button('Yazımı değerlendir'); b.clicked.connect(self.evaluate); lay.addWidget(b,alignment=Qt.AlignLeft); self.feedback=make_label('','muted',True); lay.addWidget(self.feedback); self.refresh()
    def refresh(self):
        self.combo.clear()
        for level in LEVEL_ORDER:
            if self.db.level_accessible(level):
                for l in self.db.get_lessons(level): self.combo.addItem(f"{level} • {l['title']}",(l['id'],level))
        self.combo.currentIndexChanged.connect(self.load); self.load()
    def load(self):
        if self.combo.currentData(): self.prompt.setText(self.db.get_lesson(self.combo.currentData()[0])['writing_prompt'])
    def evaluate(self):
        if not self.combo.currentData(): return
        level=self.combo.currentData()[1]; score,notes=writing_score(self.editor.toPlainText(),level); self.feedback.setText(f"Puan: %{score}\n"+'\n'.join(notes)); self.db.log_activity('Writing pratiği','writing',score,12,8)


class ReadingPage(QWidget):
    def __init__(self,db):
        super().__init__(); self.db=db; lay=QVBoxLayout(self); lay.setContentsMargins(36,30,36,30); lay.addWidget(make_label('Reading Room','pageTitle')); self.combo=QComboBox(); lay.addWidget(self.combo); self.text=make_label('','cardTitle',True); lay.addWidget(self.text); self.answer=QLineEdit(); self.answer.setPlaceholderText('Metnin ana fikrini İngilizce bir cümleyle yaz...'); lay.addWidget(self.answer); b=button('Reading puanını hesapla'); b.clicked.connect(self.evaluate); lay.addWidget(b,alignment=Qt.AlignLeft); lay.addStretch(); self.refresh()
    def refresh(self):
        self.combo.clear()
        for level in LEVEL_ORDER:
            if self.db.level_accessible(level):
                for l in self.db.get_lessons(level): self.combo.addItem(f"{level} • {l['title']}",l['id'])
        self.combo.currentIndexChanged.connect(self.load); self.load()
    def load(self):
        if self.combo.currentData(): self.text.setText(self.db.get_lesson(self.combo.currentData())['reading_text'])
    def evaluate(self):
        if not self.combo.currentData(): return
        l=self.db.get_lesson(self.combo.currentData()); score=speaking_score(l['reading_text'],self.answer.text())
        score=max(35,score) if self.answer.text().strip() else 0
        self.db.log_activity('Reading pratiği','reading',score,8,5); QMessageBox.information(self,'Reading',f'Yanıt/ana fikir benzerlik puanı: %{score}\nKendi cümlenle özetleme pratiği yapman amaçlanır.')


class ProgressPage(QWidget):
    def __init__(self,db):
        super().__init__(); self.db=db; self.root=QVBoxLayout(self); self.root.setContentsMargins(36,30,36,30); self.root.addWidget(make_label('İlerleme ve İstatistik','pageTitle')); self.body=QVBoxLayout(); self.root.addLayout(self.body); self.root.addStretch(); self.refresh()
    def refresh(self):
        clear_layout(self.body); s=self.db.stats(); p=self.db.get_profile(); f,fl=card('Genel Durum'); fl.addWidget(make_label(f"Tamamlanan ders: {s['completed']} / {s['total']}")); fl.addWidget(make_label(f"Toplam çalışma: {s['minutes']} dakika")); fl.addWidget(make_label(f"Kelime havuzu: {s['words']} • Tekrar: {s['reviews']}")); fl.addWidget(make_label(f"XP: {s['xp']} • Seri: {s['streak']} gün",'accentText')); self.body.addWidget(f)
        sf,sl=card(f"{p['current_level']} Beceri Puanları"); names={'vocabulary':'Kelime','grammar':'Grammar','reading':'Reading','listening':'Listening','speaking':'Speaking','writing':'Writing'}
        for k,v in self.db.skill_scores().items(): r=QHBoxLayout(); r.addWidget(QLabel(names[k])); pb=QProgressBar(); pb.setRange(0,100); pb.setValue(v); r.addWidget(pb,1); r.addWidget(QLabel(f'%{v}')); sl.addLayout(r)
        self.body.addWidget(sf)


class AchievementsPage(QWidget):
    def __init__(self,db):
        super().__init__(); self.db=db; outer=QVBoxLayout(self); outer.setContentsMargins(36,30,36,30); outer.addWidget(make_label('Başarımlar','pageTitle')); self.list=QVBoxLayout(); outer.addLayout(self.list); outer.addStretch(); self.refresh()
    def refresh(self):
        clear_layout(self.list)
        for a in self.db.achievements():
            f,l=card(); l.addWidget(make_label(('🏆 ' if a['unlocked'] else '🔒 ')+a['title'],'cardTitle')); l.addWidget(make_label('Açıldı' if a['unlocked'] else 'Henüz kilitli','accentText' if a['unlocked'] else 'muted')); self.list.addWidget(f)


class SettingsPage(QWidget):
    def __init__(self,db,window,app):
        super().__init__(); self.db=db; self.window=window; self.app=app; lay=QVBoxLayout(self); lay.setContentsMargins(36,30,36,30); lay.addWidget(make_label('Ayarlar','pageTitle')); f,fl=card('Profil ve Uygulama'); self.name=QLineEdit(); self.goal=QSpinBox(); self.goal.setRange(5,180); self.theme=QComboBox(); self.theme.addItems(['dark','light']); self.rate=QSpinBox(); self.rate.setRange(100,260); fl.addWidget(QLabel('Ad')); fl.addWidget(self.name); fl.addWidget(QLabel('Günlük hedef (dakika)')); fl.addWidget(self.goal); fl.addWidget(QLabel('Tema')); fl.addWidget(self.theme); fl.addWidget(QLabel('TTS konuşma hızı')); fl.addWidget(self.rate); save=button('Kaydet'); save.clicked.connect(self.save); fl.addWidget(save,alignment=Qt.AlignLeft); lay.addWidget(f); lay.addStretch(); self.refresh()
    def refresh(self):
        p=self.db.get_profile(); self.name.setText(p['name']); self.goal.setValue(p['daily_goal']); self.theme.setCurrentText(p['theme']); self.rate.setValue(p['tts_rate'])
    def save(self):
        self.db.update_profile(self.name.text(),self.goal.value(),self.theme.currentText(),self.rate.value()); self.app.setStyleSheet(get_stylesheet(self.theme.currentText())); self.window.speech.rate=self.rate.value(); QMessageBox.information(self,'Kaydedildi','Ayarlar kaydedildi.'); self.window.pages['dashboard'].refresh()


class MainWindow(QMainWindow):
    def __init__(self,db,app):
        super().__init__(); self.db=db; self.app=app; self.speech=SpeechService(db.get_profile()['tts_rate']); self.setWindowTitle('FluentPath 1.0 — A1’den C2’ye İngilizce'); self.resize(1280,800); self.setMinimumSize(1000,680)
        central=QWidget(); self.setCentralWidget(central); root=QHBoxLayout(central); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        side=QFrame(); side.setObjectName('sidebar'); side.setFixedWidth(235); sl=QVBoxLayout(side); sl.setContentsMargins(20,26,20,20); sl.addWidget(make_label('FLUENTPATH','logo')); sl.addWidget(make_label('A1 → C2 English','muted')); sl.addSpacing(16)
        self.stack=QStackedWidget(); self.pages={}
        defs=[
            ('dashboard','⌂  Ana Sayfa',lambda:DashboardPage(db,self)),('levels','▦  Dersler',lambda:LevelsPage(db,self)),('vocab','▤  Kelimeler',lambda:VocabularyPage(db)),('review','↻  Tekrar',lambda:ReviewPage(db)),('listening','▶  Listening',lambda:ListeningPage(db,self)),('speaking','◉  Speaking',lambda:SpeakingPage(db,self)),('writing','✎  Writing',lambda:WritingPage(db)),('reading','▣  Reading',lambda:ReadingPage(db)),('progress','◔  İlerleme',lambda:ProgressPage(db)),('achievements','★  Başarımlar',lambda:AchievementsPage(db)),('settings','⚙  Ayarlar',lambda:SettingsPage(db,self,app))]
        for key,label,factory in defs:
            page=factory(); self.pages[key]=page; self.stack.addWidget(page); b=QPushButton(label); b.setObjectName('navButton'); b.setCursor(Qt.PointingHandCursor); b.clicked.connect(lambda _,k=key:self.open_page(k)); sl.addWidget(b)
        sl.addStretch(); sl.addWidget(make_label('Yerel SQLite kayıt\nİnternetsiz temel kullanım','muted',True)); root.addWidget(side); root.addWidget(self.stack,1); self.open_page('dashboard')
    def run_first_setup_if_needed(self):
        if not self.db.get_profile()['setup_complete']:
            dlg=SetupDialog(self.db,self)
            if dlg.exec()!=QDialog.Accepted: return
            self.speech.rate=self.db.get_profile()['tts_rate']; self.refresh_all(); self.open_page('dashboard')
    def refresh_all(self):
        for p in self.pages.values():
            if hasattr(p,'refresh'):
                try: p.refresh()
                except Exception: pass
    def open_page(self,key):
        p=self.pages[key]
        if hasattr(p,'refresh'):
            try: p.refresh()
            except Exception: pass
        self.stack.setCurrentWidget(p)
    def open_lesson(self,lesson_id):
        if not self.db.lesson_accessible(lesson_id): QMessageBox.warning(self,'Kilitli','Önce önceki dersi tamamlamalısın.'); return
        page=LessonPage(self.db,self,lesson_id); self.stack.addWidget(page); self.stack.setCurrentWidget(page)
    def speak(self,text):
        ok,msg=self.speech.speak(text)
        if not ok: QMessageBox.information(self,'Seslendirme',msg)
