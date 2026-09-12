import json
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread, QDate
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QMainWindow,QWidget,QFrame,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QPushButton,
    QStackedWidget,QScrollArea,QProgressBar,QMessageBox,QDialog,QLineEdit,QSpinBox,
    QComboBox,QRadioButton,QButtonGroup,QTextEdit,QTableWidget,QTableWidgetItem,QHeaderView,
    QCheckBox, QAbstractItemView, QMenu, QDateEdit
)
from .curriculum import PLACEMENT_QUESTIONS, LEVELS
from .database import LEVEL_ORDER, SKILLS
from .services import SpeechService, speaking_score, writing_score
from .styles import apply_theme
from .starfield import StarfieldWidget


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
        super().__init__(parent); self.db=db; self.setWindowTitle('12/D Dil Programı — İlk Kurulum'); self.setModal(True); self.setMinimumWidth(520)
        lay=QVBoxLayout(self); lay.setContentsMargins(28,28,28,28); lay.setSpacing(14)
        lay.addWidget(make_label('12/D Dil Programı’na Hoş Geldin','pageTitle'))
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
    def __init__(self, db, window):
        super().__init__(); self.db=db; self.window=window
        outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,0)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        content=QWidget(); self.root=QVBoxLayout(content); self.root.setContentsMargins(36,30,36,32); self.root.setSpacing(18)
        scroll.setWidget(content); outer.addWidget(scroll)

        self.root.addWidget(make_label('12/D • PREMIUM ENGLISH LEARNING','pageEyebrow'))
        self.title=make_label('','pageTitle'); self.root.addWidget(self.title)
        self.subtitle=make_label('Bugün ne yapacağını düşünmek zorunda değilsin; 12/D Dil Programı sıradaki adımı seçer.','muted',True); self.root.addWidget(self.subtitle)
        self.stats_layout=QHBoxLayout(); self.stats_layout.setSpacing(12); self.root.addLayout(self.stats_layout)

        top=QHBoxLayout(); top.setSpacing(14)
        self.hero,self.hero_lay=card(); self.hero.setObjectName('heroCard'); top.addWidget(self.hero,2)
        self.goal_card,self.goal_lay=card('Bugünkü Hedef'); top.addWidget(self.goal_card,1)
        self.root.addLayout(top)

        quick,ql=card('Hızlı Çalışma')
        self.quick_grid=QGridLayout(); self.quick_grid.setHorizontalSpacing(10); self.quick_grid.setVerticalSpacing(10); ql.addLayout(self.quick_grid)
        self.root.addWidget(quick)

        middle=QHBoxLayout(); middle.setSpacing(14)
        self.skills,self.skills_lay=card('Beceri Durumu'); middle.addWidget(self.skills,1)
        self.recent,self.recent_lay=card('Son Çalışmalar'); middle.addWidget(self.recent,1)
        self.root.addLayout(middle); self.root.addStretch(); self.refresh()

    def stat(self,title,value,note):
        f,l=card(); f.setObjectName('statCard'); l.addWidget(make_label(title,'muted')); l.addWidget(make_label(str(value),'statValue')); l.addWidget(make_label(note,'muted')); return f

    def refresh(self):
        clear_layout(self.stats_layout); clear_layout(self.hero_lay); clear_layout(self.goal_lay); clear_layout(self.quick_grid); clear_layout(self.skills_lay); clear_layout(self.recent_lay)
        p=self.db.get_profile(); st=self.db.stats(); self.title.setText(f"Merhaba, {p['name']} 👋")
        self.stats_layout.addWidget(self.stat('Seviye',p['current_level'],'şu anki rota'))
        self.stats_layout.addWidget(self.stat('Toplam XP',p['xp'],'öğrenme puanı'))
        self.stats_layout.addWidget(self.stat('🔥 Seri',p['streak'],'gün'))
        self.stats_layout.addWidget(self.stat('Tekrar',len(self.db.due_words()),'bugün bekliyor'))

        nxt=self.db.next_lesson()
        self.hero_lay.addWidget(make_label('SIRADAKİ ADIM','accentText'))
        if nxt:
            self.hero_lay.addWidget(make_label(f"{nxt['level_code']} • {nxt['title']}",'heroTitle',True))
            self.hero_lay.addWidget(make_label(nxt['description'],'muted',True))
            row=QHBoxLayout(); start=button('Şimdi derse başla →'); start.clicked.connect(lambda _,lid=nxt['id']:self.window.open_lesson(lid)); row.addWidget(start)
            all_lessons=button('Tüm dersler',False); all_lessons.clicked.connect(lambda:self.window.open_page('levels')); row.addWidget(all_lessons); row.addStretch(); self.hero_lay.addLayout(row)
        else:
            self.hero_lay.addWidget(make_label('Erişilebilir tüm dersleri tamamladın 🎉','cardTitle',True))
            b=button('İlerlemeyi görüntüle'); b.clicked.connect(lambda:self.window.open_page('progress')); self.hero_lay.addWidget(b,alignment=Qt.AlignLeft)

        mins=self.db.today_minutes(); goal=p['daily_goal']; today=self.db.today_summary()
        self.goal_lay.addWidget(make_label(f'{mins} / {goal} dakika','cardTitle'))
        bar=QProgressBar(); bar.setRange(0,max(1,goal)); bar.setValue(min(mins,goal)); self.goal_lay.addWidget(bar)
        self.goal_lay.addWidget(make_label(f"Bugün +{today['xp']} XP • {today['activities']} çalışma",'muted'))
        remain=max(0,goal-mins)
        self.goal_lay.addWidget(make_label('Hedef tamamlandı ✓' if remain==0 else f'Hedefe {remain} dakika kaldı.','accentText' if remain==0 else 'muted'))

        actions=[
            ('↻  Kelime Tekrarı',f"{len(self.db.due_words())} kart bekliyor",'review'),
            ('▶  Listening','Duyduğunu yakala','listening'),
            ('◉  Speaking','Sesli pratik yap','speaking'),
            ('✎  Writing','Kısa metin yaz','writing'),
        ]
        for i,(title,note,key) in enumerate(actions):
            b=QPushButton(f'{title}\n{note}'); b.setObjectName('quickButton'); b.setCursor(Qt.PointingHandCursor); b.clicked.connect(lambda _,k=key:self.window.open_page(k)); self.quick_grid.addWidget(b,i//2,i%2)

        scores=self.db.skill_scores(); names={'vocabulary':'Kelime','grammar':'Grammar','reading':'Reading','listening':'Listening','speaking':'Speaking','writing':'Writing'}
        for sk in SKILLS:
            r=QHBoxLayout(); lab=QLabel(names[sk]); lab.setFixedWidth(72); r.addWidget(lab); pb=QProgressBar(); pb.setRange(0,100); pb.setValue(scores[sk]); r.addWidget(pb,1); r.addWidget(QLabel(f"%{scores[sk]}")); self.skills_lay.addLayout(r)

        recent=self.db.recent_activities(6)
        if not recent: self.recent_lay.addWidget(make_label('Henüz çalışma kaydı yok. İlk dersini tamamlayarak başla.','muted',True))
        for x in recent:
            when=x['created_at'][5:16].replace('T','  '); score=f" • %{x['score']}" if x['score'] is not None else ''
            self.recent_lay.addWidget(make_label(f"{x['activity']}{score}",'cardTitle',True)); self.recent_lay.addWidget(make_label(f"{when} • {x['minutes']} dk • +{x['xp']} XP",'muted'))


class LevelsPage(QWidget):
    def __init__(self, db, window):
        super().__init__(); self.db=db; self.window=window
        outer=QVBoxLayout(self); outer.setContentsMargins(36,30,36,30); outer.setSpacing(12)
        outer.addWidget(make_label('Dersler','pageTitle'))
        outer.addWidget(make_label('Seviyeni seç, ders ara ve kaldığın yerden devam et.','muted'))

        controls=QHBoxLayout();
        self.level_combo=QComboBox(); self.level_combo.setMinimumWidth(170); controls.addWidget(self.level_combo)
        self.search=QLineEdit(); self.search.setObjectName('searchBox'); self.search.setPlaceholderText('🔎 Ders ara...'); controls.addWidget(self.search,1)
        self.status=QComboBox(); self.status.addItems(['Tümü','Tamamlanmadı','Tamamlandı','Erişilebilir']); controls.addWidget(self.status)
        outer.addLayout(controls)

        self.summary=make_label('','muted',True); outer.addWidget(self.summary)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        self.content=QWidget(); self.list=QVBoxLayout(self.content); self.list.setSpacing(11); scroll.setWidget(self.content); outer.addWidget(scroll)

        self.level_combo.currentIndexChanged.connect(self.render_lessons); self.search.textChanged.connect(self.render_lessons); self.status.currentIndexChanged.connect(self.render_lessons)
        self._loaded=False; self.refresh()

    def refresh(self):
        current=self.db.get_profile()['current_level']; previous=self.level_combo.currentData() if self._loaded else current
        self.level_combo.blockSignals(True); self.level_combo.clear()
        for lvl in LEVEL_ORDER:
            accessible=self.db.level_accessible(lvl); self.level_combo.addItem(f"{lvl} {'✓' if accessible else '🔒'}",lvl)
            if not accessible:
                item=self.level_combo.model().item(self.level_combo.count()-1)
                if item: item.setEnabled(False)
        idx=self.level_combo.findData(previous if previous in LEVEL_ORDER else current)
        if idx<0 or not self.db.level_accessible(self.level_combo.itemData(idx)): idx=self.level_combo.findData(current)
        self.level_combo.setCurrentIndex(max(0,idx)); self.level_combo.blockSignals(False); self._loaded=True; self.render_lessons()

    def render_lessons(self):
        if not self._loaded: return
        clear_layout(self.list); level=self.level_combo.currentData()
        if not level: return
        lessons=self.db.get_lessons(level); completed=sum(1 for x in lessons if x['completed']); pct=round(completed/max(1,len(lessons))*100)
        self.summary.setText(f'{level}: {completed}/{len(lessons)} ders tamamlandı • %{pct} ilerleme')
        query=self.search.text().strip().lower(); status=self.status.currentText()
        shown=0
        for l in lessons:
            accessible=self.db.lesson_accessible(l['id']); done=bool(l['completed'])
            if query and query not in l['title'].lower() and query not in l['description'].lower(): continue
            if status=='Tamamlanmadı' and done: continue
            if status=='Tamamlandı' and not done: continue
            if status=='Erişilebilir' and not accessible: continue
            shown+=1; f,lay=card(); row=QHBoxLayout();
            num=make_label('✓' if done else ('🔒' if not accessible else str(l['position'])),'lessonNumber'); num.setFixedWidth(54); row.addWidget(num)
            v=QVBoxLayout(); v.addWidget(make_label(l['title'],'cardTitle')); v.addWidget(make_label(l['description'],'muted',True))
            meta=[]
            if l['best_score']: meta.append(f"En iyi %{l['best_score']}")
            if l['attempts']: meta.append(f"{l['attempts']} deneme")
            if meta: v.addWidget(make_label(' • '.join(meta),'accentText'))
            row.addLayout(v,1); b=button('Tekrar aç' if done else ('Başla' if accessible else 'Kilitli'),not done and accessible); b.setEnabled(accessible)
            if accessible: b.clicked.connect(lambda _,lid=l['id']:self.window.open_lesson(lid))
            row.addWidget(b); lay.addLayout(row); self.list.addWidget(f)
        if shown==0:
            f,l=card(); l.addWidget(make_label('Bu filtrelere uyan ders bulunamadı.','cardTitle')); l.addWidget(make_label('Arama metnini veya durum filtresini değiştirebilirsin.','muted')); self.list.addWidget(f)
        self.list.addStretch()

    def focus_search(self):
        self.search.setFocus(); self.search.selectAll()


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
    def __init__(self, db, window):
        super().__init__(); self.db=db; self.window=window
        lay=QVBoxLayout(self); lay.setContentsMargins(36,30,36,30); lay.setSpacing(12)
        lay.addWidget(make_label('Kelime Merkezi','pageTitle'))
        self.summary=make_label('','muted'); lay.addWidget(self.summary)
        tools=QHBoxLayout(); self.search=QLineEdit(); self.search.setObjectName('searchBox'); self.search.setPlaceholderText('🔎 İngilizce veya Türkçe kelime ara...'); tools.addWidget(self.search,1); self.favs=QCheckBox('Sadece favoriler'); tools.addWidget(self.favs); lay.addLayout(tools)
        self.table=QTableWidget(0,6); self.table.setHorizontalHeaderLabels(['★','Seviye','Kelime','Türkçe','Sonraki tekrar','Son sonuç']); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows); self.table.verticalHeader().setVisible(False); lay.addWidget(self.table)
        hint=make_label('İpucu: ★ sütununa tıklayarak favorile. Kelimeye çift tıklayarak telaffuzunu dinle.','muted',True); lay.addWidget(hint)
        self.search.textChanged.connect(self.render); self.favs.toggled.connect(self.render); self.table.cellClicked.connect(self.clicked); self.table.cellDoubleClicked.connect(self.double_clicked); self.rows=[]

    def refresh(self):
        self.words=list(self.db.all_words()); self.render()

    def render(self):
        query=self.search.text().strip().lower() if hasattr(self,'search') else ''; fav_only=self.favs.isChecked() if hasattr(self,'favs') else False
        self.rows=[w for w in getattr(self,'words',[]) if (not query or query in w['word'].lower() or query in w['translation'].lower()) and (not fav_only or w['favorite'])]
        due=len(self.db.due_words()); self.summary.setText(f'{len(getattr(self,"words",[]))} kelime • {due} tekrar bekliyor • {len(self.rows)} sonuç gösteriliyor')
        self.table.setRowCount(len(self.rows))
        for r,w in enumerate(self.rows):
            vals=['★' if w['favorite'] else '☆',w['level_code'],w['word'],w['translation'],w['due_date'],w['last_result'] or '—']
            for c,v in enumerate(vals): self.table.setItem(r,c,QTableWidgetItem(str(v)))

    def clicked(self,row,col):
        if col==0 and 0<=row<len(self.rows): self.db.toggle_favorite(self.rows[row]['id']); self.refresh()

    def double_clicked(self,row,col):
        if 0<=row<len(self.rows) and col in (2,3): self.window.speak(self.rows[row]['word'])


class ReviewPage(QWidget):
    def __init__(self,db):
        super().__init__(); self.db=db; self.words=[]; self.index=0; self.revealed=False
        lay=QVBoxLayout(self); lay.setContentsMargins(36,30,36,30); lay.setSpacing(14); lay.addWidget(make_label('Akıllı Tekrar','pageTitle'))
        self.info=make_label('','muted'); lay.addWidget(self.info); self.progress=QProgressBar(); lay.addWidget(self.progress)
        self.f,self.fl=card(); lay.addWidget(self.f); lay.addStretch(); self.refresh()
    def refresh(self):
        self.words=list(self.db.due_words()); self.index=0; self.progress.setRange(0,max(1,len(self.words))); self.render()
    def render(self):
        clear_layout(self.fl); self.revealed=False; self.progress.setValue(min(self.index,len(self.words)))
        if not self.words or self.index>=len(self.words):
            self.info.setText('Bugün için bekleyen tekrar kalmadı 🎉'); self.fl.addWidget(make_label('Harika! Bir sonraki tekrar zamanı gelince kelimeler burada görünecek.','cardTitle',True)); return
        w=self.words[self.index]; self.info.setText(f'{self.index+1}/{len(self.words)} • Önce anlamı hatırlamaya çalış')
        self.fl.addWidget(make_label(w['word'],'pageTitle')); self.answer=make_label('Cevap gizli','muted',True); self.fl.addWidget(self.answer)
        rb=button('Anlamı göster',False); rb.clicked.connect(lambda:self.reveal(w)); self.fl.addWidget(rb,alignment=Qt.AlignLeft)
        self.rate_row=QHBoxLayout(); self.rate_buttons=[]
        for label,q in [('Zor','hard'),('Orta','medium'),('Kolay','easy')]:
            b=button(label,q=='easy'); b.setEnabled(False); b.clicked.connect(lambda _,quality=q:self.rate(quality)); self.rate_buttons.append(b); self.rate_row.addWidget(b)
        self.fl.addLayout(self.rate_row); self.fl.addWidget(make_label('Cevabı gördükten sonra ne kadar iyi hatırladığını seç.','muted'))
    def reveal(self,w):
        self.revealed=True; self.answer.setText(f"{w['translation']}\n\nÖrnek: {w['example'] or '—'}")
        for b in self.rate_buttons: b.setEnabled(True)
    def rate(self,q):
        if not self.revealed: return
        self.db.review_word(self.words[self.index]['id'],q); self.index+=1; self.render()


class ListeningPage(QWidget):
    def __init__(self,db,window):
        super().__init__(); self.db=db; self.window=window; lay=QVBoxLayout(self); lay.setContentsMargins(36,30,36,30); lay.addWidget(make_label('Listening Lab','pageTitle'))
        self.combo=QComboBox(); self.combo.currentIndexChanged.connect(self.load); lay.addWidget(self.combo); self.text=make_label('','muted',True); self.text.setVisible(False); lay.addWidget(self.text)
        row=QHBoxLayout(); play=button('▶ Dinle'); play.clicked.connect(self.play); row.addWidget(play); show=button('Metni göster/gizle',False); show.clicked.connect(lambda:self.text.setVisible(not self.text.isVisible())); row.addWidget(show); row.addStretch(); lay.addLayout(row)
        self.check=QLineEdit(); self.check.setPlaceholderText('Duyduğun cümleden hatırladığın kısmı İngilizce yaz...'); lay.addWidget(self.check); score=button('Kendini değerlendir',False); score.clicked.connect(self.evaluate); lay.addWidget(score,alignment=Qt.AlignLeft); lay.addStretch(); self.refresh()
    def refresh(self):
        self.combo.clear();
        for level in LEVEL_ORDER:
            if self.db.level_accessible(level):
                for l in self.db.get_lessons(level): self.combo.addItem(f"{level} • {l['title']}",l['id'])
        self.load()
    def load(self):
        if self.combo.currentData(): self.text.setText(self.db.get_lesson(self.combo.currentData())['listening_text'])
    def play(self):
        if not self.combo.currentData(): return
        self.window.speak(self.db.get_lesson(self.combo.currentData())['listening_text'])
    def evaluate(self):
        if not self.combo.currentData(): return
        target=self.db.get_lesson(self.combo.currentData())['listening_text']; score=speaking_score(target,self.check.text()); self.db.log_activity('Listening pratiği','listening',score,8,5); QMessageBox.information(self,'Listening',f'Yakalama puanın: %{score}\nBu puan yazdığın ifadelerin hedef metinle benzerliğine göre hesaplandı.')


class MicWorker(QObject):
    finished = Signal(bool, str)

    def __init__(self, speech_service):
        super().__init__()
        self.speech_service = speech_service

    @Slot()
    def run(self):
        ok, text = self.speech_service.listen_once()
        self.finished.emit(ok, text)


class SpeakingPage(QWidget):
    def __init__(self,db,window):
        super().__init__(); self.db=db; self.window=window; self.mic_thread=None; self.mic_worker=None
        lay=QVBoxLayout(self); lay.setContentsMargins(36,30,36,30); lay.addWidget(make_label('Speaking Studio','pageTitle'))
        lay.addWidget(make_label('Mikrofon kaydı PyAudio kullanmaz. Butona bastıktan sonra yaklaşık 7 saniye İngilizce konuş.','muted',True))
        self.combo=QComboBox(); self.combo.currentIndexChanged.connect(self.load); lay.addWidget(self.combo); self.target=make_label('','cardTitle',True); lay.addWidget(self.target)
        row=QHBoxLayout(); hear=button('🔊 Örneği dinle',False); hear.clicked.connect(lambda:self.window.speak(self.target.text())); row.addWidget(hear); self.mic_button=button('🎤 7 sn kayıt ve algıla'); self.mic_button.clicked.connect(self.mic); row.addWidget(self.mic_button); row.addStretch(); lay.addLayout(row)
        self.mic_status=make_label('Mikrofon hazır.','muted',True); lay.addWidget(self.mic_status)
        self.input=QLineEdit(); self.input.setPlaceholderText('Mikrofon yoksa söylediğin/çalıştığın cümleyi buraya yaz...'); lay.addWidget(self.input); ev=button('Telaffuz/benzerlik puanını hesapla'); ev.clicked.connect(self.evaluate); lay.addWidget(ev,alignment=Qt.AlignLeft); self.result=make_label('','accentText',True); lay.addWidget(self.result); lay.addStretch(); self.refresh()
    def refresh(self):
        self.combo.clear()
        for level in LEVEL_ORDER:
            if self.db.level_accessible(level):
                for l in self.db.get_lessons(level): self.combo.addItem(f"{level} • {l['title']}",l['id'])
        self.load()
    def load(self):
        if self.combo.currentData(): self.target.setText(self.db.get_lesson(self.combo.currentData())['speaking_prompt'])
    def mic(self):
        if self.mic_thread is not None and self.mic_thread.isRunning():
            return
        self.mic_button.setEnabled(False)
        self.mic_button.setText('🎤 Dinleniyor...')
        self.mic_status.setText('Şimdi konuş. Kayıt yaklaşık 7 saniye sürecek...')
        self.mic_thread=QThread(self)
        self.mic_worker=MicWorker(self.window.speech)
        self.mic_worker.moveToThread(self.mic_thread)
        self.mic_thread.started.connect(self.mic_worker.run)
        self.mic_worker.finished.connect(self._mic_finished)
        self.mic_worker.finished.connect(self.mic_thread.quit)
        self.mic_thread.finished.connect(self._mic_cleanup)
        self.mic_thread.start()
    @Slot(bool, str)
    def _mic_finished(self,ok,text):
        self.mic_button.setEnabled(True)
        self.mic_button.setText('🎤 7 sn kayıt ve algıla')
        if ok:
            self.input.setText(text)
            self.mic_status.setText(f'Algılanan: {text}')
            self.evaluate()
        else:
            self.mic_status.setText(text)
            QMessageBox.information(self,'Mikrofon',text)
    @Slot()
    def _mic_cleanup(self):
        if self.mic_worker is not None:
            self.mic_worker.deleteLater()
        if self.mic_thread is not None:
            self.mic_thread.deleteLater()
        self.mic_worker=None
        self.mic_thread=None
    def evaluate(self):
        score=speaking_score(self.target.text(),self.input.text()); self.result.setText(f'Benzerlik puanı: %{score}'); self.db.log_activity('Speaking pratiği','speaking',score,10,5)


class WritingPage(QWidget):
    def __init__(self,db):
        super().__init__(); self.db=db; lay=QVBoxLayout(self); lay.setContentsMargins(36,30,36,30); lay.addWidget(make_label('Writing Coach','pageTitle')); self.combo=QComboBox(); self.combo.currentIndexChanged.connect(self.load); lay.addWidget(self.combo); self.prompt=make_label('','cardTitle',True); lay.addWidget(self.prompt); self.editor=QTextEdit(); self.editor.setPlaceholderText('İngilizce metnini yaz...'); lay.addWidget(self.editor,1); b=button('Yazımı değerlendir'); b.clicked.connect(self.evaluate); lay.addWidget(b,alignment=Qt.AlignLeft); self.feedback=make_label('','muted',True); lay.addWidget(self.feedback); self.refresh()
    def refresh(self):
        self.combo.clear()
        for level in LEVEL_ORDER:
            if self.db.level_accessible(level):
                for l in self.db.get_lessons(level): self.combo.addItem(f"{level} • {l['title']}",(l['id'],level))
        self.load()
    def load(self):
        if self.combo.currentData(): self.prompt.setText(self.db.get_lesson(self.combo.currentData()[0])['writing_prompt'])
    def evaluate(self):
        if not self.combo.currentData(): return
        level=self.combo.currentData()[1]; score,notes=writing_score(self.editor.toPlainText(),level); self.feedback.setText(f"Puan: %{score}\n"+'\n'.join(notes)); self.db.log_activity('Writing pratiği','writing',score,12,8)


class ReadingPage(QWidget):
    def __init__(self,db):
        super().__init__(); self.db=db; lay=QVBoxLayout(self); lay.setContentsMargins(36,30,36,30); lay.addWidget(make_label('Reading Room','pageTitle')); self.combo=QComboBox(); self.combo.currentIndexChanged.connect(self.load); lay.addWidget(self.combo); self.text=make_label('','cardTitle',True); lay.addWidget(self.text); self.answer=QLineEdit(); self.answer.setPlaceholderText('Metnin ana fikrini İngilizce bir cümleyle yaz...'); lay.addWidget(self.answer); b=button('Reading puanını hesapla'); b.clicked.connect(self.evaluate); lay.addWidget(b,alignment=Qt.AlignLeft); lay.addStretch(); self.refresh()
    def refresh(self):
        self.combo.clear()
        for level in LEVEL_ORDER:
            if self.db.level_accessible(level):
                for l in self.db.get_lessons(level): self.combo.addItem(f"{level} • {l['title']}",l['id'])
        self.load()
    def load(self):
        if self.combo.currentData(): self.text.setText(self.db.get_lesson(self.combo.currentData())['reading_text'])
    def evaluate(self):
        if not self.combo.currentData(): return
        l=self.db.get_lesson(self.combo.currentData()); score=speaking_score(l['reading_text'],self.answer.text())
        score=max(35,score) if self.answer.text().strip() else 0
        self.db.log_activity('Reading pratiği','reading',score,8,5); QMessageBox.information(self,'Reading',f'Yanıt/ana fikir benzerlik puanı: %{score}\nKendi cümlenle özetleme pratiği yapman amaçlanır.')


class ProgressPage(QWidget):
    def __init__(self,db):
        super().__init__(); self.db=db
        outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame); cont=QWidget(); self.root=QVBoxLayout(cont); self.root.setContentsMargins(36,30,36,32); self.root.setSpacing(14); scroll.setWidget(cont); outer.addWidget(scroll)
        self.root.addWidget(make_label('İlerleme ve İstatistik','pageTitle')); self.body=QVBoxLayout(); self.root.addLayout(self.body); self.root.addStretch(); self.refresh()
    def refresh(self):
        clear_layout(self.body); s=self.db.stats(); p=self.db.get_profile(); level=self.db.current_level_progress();
        top=QHBoxLayout();
        for title,val,note in [('Ders',f"{s['completed']}/{s['total']}",'toplam'),('Çalışma',f"{s['minutes']} dk",'toplam'),('Kelime',s['words'],'havuzda'),('XP',s['xp'],'toplam')]:
            f,l=card(); l.addWidget(make_label(title,'muted')); l.addWidget(make_label(str(val),'statValue')); l.addWidget(make_label(note,'muted')); top.addWidget(f)
        self.body.addLayout(top)
        lf,ll=card(f"{p['current_level']} Seviye İlerlemesi"); ll.addWidget(make_label(f"{level['completed']} / {level['total']} ders • %{level['percent']}",'cardTitle')); pb=QProgressBar(); pb.setRange(0,100); pb.setValue(level['percent']); ll.addWidget(pb); self.body.addWidget(lf)
        sf,sl=card(f"{p['current_level']} Beceri Puanları"); names={'vocabulary':'Kelime','grammar':'Grammar','reading':'Reading','listening':'Listening','speaking':'Speaking','writing':'Writing'}
        for k,v in self.db.skill_scores().items(): r=QHBoxLayout(); lab=QLabel(names[k]); lab.setFixedWidth(75); r.addWidget(lab); pb=QProgressBar(); pb.setRange(0,100); pb.setValue(v); r.addWidget(pb,1); r.addWidget(QLabel(f'%{v}')); sl.addLayout(r)
        self.body.addWidget(sf)
        wf,wl=card('Son 7 Gün');
        week=self.db.weekly_minutes(); peak=max([x['minutes'] for x in week] or [1])
        for x in week:
            r=QHBoxLayout(); lab=QLabel(x['label']); lab.setFixedWidth(70); r.addWidget(lab); pb=QProgressBar(); pb.setRange(0,max(1,peak)); pb.setValue(x['minutes']); pb.setFormat(f"{x['minutes']} dk"); r.addWidget(pb,1); wl.addLayout(r)
        self.body.addWidget(wf)


class AchievementsPage(QWidget):
    def __init__(self,db):
        super().__init__(); self.db=db; outer=QVBoxLayout(self); outer.setContentsMargins(36,30,36,30); outer.addWidget(make_label('Başarımlar','pageTitle')); self.list=QVBoxLayout(); outer.addLayout(self.list); outer.addStretch(); self.refresh()
    def refresh(self):
        clear_layout(self.list)
        for a in self.db.achievements():
            f,l=card(); l.addWidget(make_label(('🏆 ' if a['unlocked'] else '🔒 ')+a['title'],'cardTitle')); l.addWidget(make_label('Açıldı' if a['unlocked'] else 'Henüz kilitli','accentText' if a['unlocked'] else 'muted')); self.list.addWidget(f)


class SettingsPage(QWidget):
    def __init__(self,db,window,app):
        super().__init__(); self.db=db; self.window=window; self.app=app
        lay=QVBoxLayout(self); lay.setContentsMargins(36,30,36,30); lay.setSpacing(14); lay.addWidget(make_label('Ayarlar','pageTitle'))
        f,fl=card('Profil ve Uygulama')
        self.name=QLineEdit(); self.goal=QSpinBox(); self.goal.setRange(5,180); self.theme=QComboBox(); self.theme.addItem('Koyu tema','dark'); self.theme.addItem('Açık tema','light'); self.rate=QSpinBox(); self.rate.setRange(100,260)
        fl.addWidget(QLabel('Ad')); fl.addWidget(self.name); fl.addWidget(QLabel('Günlük hedef (dakika)')); fl.addWidget(self.goal); fl.addWidget(QLabel('Görünüm')); fl.addWidget(self.theme); fl.addWidget(QLabel('İngilizce ses hızı')); fl.addWidget(self.rate)
        row=QHBoxLayout(); save=button('Ayarları kaydet'); save.clicked.connect(self.save); row.addWidget(save); test=button('🔊 Sesi test et',False); test.clicked.connect(lambda:self.window.speak('Hello! Welcome to the 12 D Language Program.')); row.addWidget(test); row.addStretch(); fl.addLayout(row); lay.addWidget(f)

        learning,ll=card('Öğrenme Ayarları'); ll.addWidget(make_label('Seviye tespit sınavını yeniden çalıştırırsan mevcut ders ilerlemen silinmez; yalnızca erişilebilir seviye rotan güncellenir.','muted',True)); retake=button('Seviye testini tekrar yap',False); retake.clicked.connect(self.retake); ll.addWidget(retake,alignment=Qt.AlignLeft); lay.addWidget(learning)
        info,il=card('Klavye Kısayolları'); il.addWidget(make_label('Ctrl+1 Ana Sayfa  •  Ctrl+2 Dersler  •  Ctrl+3 Kelimeler  •  Ctrl+R Tekrar  •  Ctrl+F Ders Ara  •  F5 Yenile','muted',True)); lay.addWidget(info); lay.addStretch(); self.refresh()
    def refresh(self):
        p=self.db.get_profile(); self.name.setText(p['name']); self.goal.setValue(p['daily_goal']); idx=self.theme.findData(p['theme']); self.theme.setCurrentIndex(max(0,idx)); self.rate.setValue(p['tts_rate'])
    def save(self):
        theme=self.theme.currentData(); self.db.update_profile(self.name.text(),self.goal.value(),theme,self.rate.value()); apply_theme(self.app,theme); self.window.starfield.set_theme(theme); self.window.speech.rate=self.rate.value(); self.window.refresh_all(); QMessageBox.information(self,'Kaydedildi','Tema dahil tüm ayarlar uygulandı ve kaydedildi.')
    def retake(self):
        p=self.db.get_profile(); dlg=PlacementDialog(self.db,p['name'],p['daily_goal'],self)
        if dlg.exec()==QDialog.Accepted: self.window.refresh_all(); self.window.open_page('dashboard')


class ProfileCreateDialog(QDialog):
    def __init__(self, db, parent=None, mandatory=False):
        super().__init__(parent)
        self.db=db
        self.created_profile_id=None
        self.mandatory=mandatory

        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle(
            '12/D Dil Programı — İlk Profilini Oluştur'
            if mandatory else
            'Yeni Profil Oluştur'
        )
        self.setMinimumWidth(540)

        lay=QVBoxLayout(self)
        lay.setContentsMargins(30,30,30,28)
        lay.setSpacing(13)

        if mandatory:
            lay.addWidget(make_label('Önce Profilini Oluştur','pageTitle'))
            lay.addWidget(make_label(
                '12/D Dil Programı’nı kullanabilmek için bir profil oluşturman gerekiyor. '
                'Bu işlem yalnızca ilk açılışta zorunludur. Profil oluşturulduktan sonra '
                'sonraki açılışlarda doğrudan ana ekrana geçilir.',
                'muted', True
            ))
            notice=QFrame()
            notice.setObjectName('heroCard')
            nl=QVBoxLayout(notice)
            nl.setContentsMargins(16,13,16,13)
            nl.addWidget(make_label(
                '🔒 Profil oluşturulmadan derslere, sınıflara ve diğer bölümlere erişilemez.',
                'accentText', True
            ))
            lay.addWidget(notice)
        else:
            lay.addWidget(make_label('Yeni Profil','pageTitle'))
            lay.addWidget(make_label(
                'Her profil kendi seviye, XP, ders ilerlemesi, kelime ve tekrar '
                'verilerini ayrı tutar.',
                'muted', True
            ))

        lay.addWidget(QLabel('Profil adı'))
        self.name=QLineEdit()
        self.name.setPlaceholderText('Örn. Pelin Öğretmen')
        self.name.setMinimumHeight(42)
        lay.addWidget(self.name)

        lay.addWidget(QLabel('Profil türü'))
        self.role=QComboBox()
        self.role.addItems(['Öğretmen','Öğrenci'])
        self.role.setMinimumHeight(40)
        lay.addWidget(self.role)

        lay.addWidget(QLabel('Başlangıç seviyesi'))
        self.level=QComboBox()
        self.level.addItems(LEVEL_ORDER)
        self.level.setMinimumHeight(40)
        lay.addWidget(self.level)

        lay.addWidget(QLabel('Günlük hedef (dakika)'))
        self.goal=QSpinBox()
        self.goal.setRange(5,180)
        self.goal.setValue(20)
        self.goal.setMinimumHeight(40)
        lay.addWidget(self.goal)

        row=QHBoxLayout()
        row.addStretch()

        cancel=button('Programdan Çık' if mandatory else 'Vazgeç',False)
        if mandatory:
            cancel.setToolTip('Profil oluşturmadan ana programa geçilemez.')
        cancel.clicked.connect(self.reject)
        row.addWidget(cancel)

        save=button('Profili Oluştur ve Devam Et →' if mandatory else 'Profili Oluştur')
        save.clicked.connect(self.create)
        row.addWidget(save)
        lay.addLayout(row)

        self.name.setFocus()

    def create(self):
        try:
            self.created_profile_id=self.db.create_profile(
                self.name.text(),
                self.role.currentText(),
                self.level.currentText(),
                self.goal.value()
            )
        except ValueError as e:
            QMessageBox.warning(self,'Profil',str(e))
            self.name.setFocus()
            return

        self.db.switch_profile(self.created_profile_id)
        self.accept()


class ProfileManagerDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self.profile_changed=False
        self.setWindowTitle('Profil Yönetimi'); self.setMinimumSize(820,520)
        lay=QVBoxLayout(self); lay.setContentsMargins(24,24,24,24); lay.setSpacing(12)
        lay.addWidget(make_label('Profil Yönetimi','pageTitle'))
        lay.addWidget(make_label('Öğretmen ve öğrenci profilleri arasında geçiş yapabilir, yeni profil oluşturabilirsin.','muted',True))
        self.table=QTableWidget(0,6); self.table.setHorizontalHeaderLabels(['Aktif','Profil','Rol','Seviye','XP','Seri'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows); self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); self.table.verticalHeader().setVisible(False)
        lay.addWidget(self.table,1)
        row=QHBoxLayout(); new=button('+ Yeni Profil'); new.clicked.connect(self.new_profile); row.addWidget(new)
        switch=button('⇄ Seçili Profile Geç',False); switch.clicked.connect(self.switch); row.addWidget(switch)
        delete=button('Profili Sil',False); delete.clicked.connect(self.delete); row.addWidget(delete); row.addStretch()
        close=button('Kapat',False); close.clicked.connect(self.accept); row.addWidget(close); lay.addLayout(row)
        self.refresh()
    def refresh(self):
        self.rows=list(self.db.list_profiles()); self.table.setRowCount(len(self.rows))
        for r,p in enumerate(self.rows):
            vals=['●' if p['active'] else '',p['name'],p['role'],p['current_level'],p['xp'],f"{p['streak']} gün"]
            for c,v in enumerate(vals): self.table.setItem(r,c,QTableWidgetItem(str(v)))
        if self.rows: self.table.selectRow(0)
    def selected(self):
        row=self.table.currentRow(); return self.rows[row] if 0<=row<len(self.rows) else None
    def new_profile(self):
        dlg=ProfileCreateDialog(self.db,self)
        if dlg.exec()==QDialog.Accepted:
            self.db.switch_profile(dlg.created_profile_id); self.profile_changed=True; self.refresh()
    def switch(self):
        p=self.selected()
        if not p: return
        self.db.switch_profile(p['id']); self.profile_changed=True; self.refresh()
    def delete(self):
        p=self.selected()
        if not p:
            return

        box=QMessageBox(self)
        box.setWindowTitle('Profili Sil')
        box.setIcon(QMessageBox.Icon.Warning)
        box.setText('Bu profili silmek istediğinize emin misiniz?')
        box.setInformativeText(
            f"Profil: {p['name']}\n\n"
            "Bu profile ait ders ilerlemesi, XP, kelimeler, tekrarlar, "
            "istatistikler ve profile bağlı sınıf verileri de silinecektir."
        )
        box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        box.setDefaultButton(QMessageBox.StandardButton.No)

        yes_button=box.button(QMessageBox.StandardButton.Yes)
        no_button=box.button(QMessageBox.StandardButton.No)
        if yes_button:
            yes_button.setText('Evet, Profili Sil')
        if no_button:
            no_button.setText('Hayır')

        if box.exec()!=QMessageBox.StandardButton.Yes:
            return

        try:
            profiles_remain=self.db.delete_profile(p['id'])
        except ValueError as e:
            QMessageBox.warning(self,'Profil',str(e))
            return

        self.profile_changed=True

        # Son profil de silindiyse ana pencerenin "profil yok" durumunda
        # refresh etmeye çalışmasını engellemek için dialogu hemen kapat.
        if not profiles_remain:
            self.accept()
            return

        self.refresh()


class ClassCreateDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self.class_id=None
        self.setWindowTitle('Yeni Sınıf Oluştur'); self.setMinimumWidth(520)
        lay=QVBoxLayout(self); lay.setContentsMargins(26,26,26,26); lay.setSpacing(12)
        lay.addWidget(make_label('Yeni Sınıf','pageTitle'))
        lay.addWidget(make_label('Sınıfı oluşturduktan sonra o sınıfta hangi derslerin hangi tarihte işleneceğini planlayabilirsin.','muted',True))
        lay.addWidget(QLabel('Sınıf adı'))
        self.name=QLineEdit(); self.name.setPlaceholderText('Örn. 12/D'); lay.addWidget(self.name)
        lay.addWidget(QLabel('İngilizce seviyesi'))
        self.level=QComboBox(); self.level.addItems(LEVEL_ORDER); lay.addWidget(self.level)
        lay.addWidget(QLabel('Eğitim-öğretim yılı'))
        self.year=QLineEdit(); self.year.setPlaceholderText('Örn. 2026-2027'); lay.addWidget(self.year)
        lay.addWidget(QLabel('Sınıf notu'))
        self.notes=QTextEdit(); self.notes.setMaximumHeight(90); self.notes.setPlaceholderText('Örn. Haftada 4 saat İngilizce'); lay.addWidget(self.notes)
        row=QHBoxLayout(); row.addStretch(); cancel=button('Vazgeç',False); cancel.clicked.connect(self.reject); row.addWidget(cancel); save=button('Sınıfı Oluştur'); save.clicked.connect(self.create); row.addWidget(save); lay.addLayout(row)
    def create(self):
        try: self.class_id=self.db.create_class(self.name.text(),self.level.currentText(),self.year.text(),self.notes.toPlainText())
        except ValueError as e: QMessageBox.warning(self,'Sınıf',str(e)); return
        self.accept()


class ClassManagerDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent); self.db=db; self.current_class_id=None; self.plan_rows=[]
        self.setWindowTitle('Sınıf ve Ders Planı Yönetimi'); self.setMinimumSize(1120,720)
        root=QVBoxLayout(self); root.setContentsMargins(24,22,24,22); root.setSpacing(12)
        head=QHBoxLayout(); titlebox=QVBoxLayout(); titlebox.addWidget(make_label('Sınıf Yönetimi','pageTitle')); titlebox.addWidget(make_label('Sınıfları oluştur, seviyeyi belirle ve hangi dersin ne zaman işleneceğini planla.','muted',True)); head.addLayout(titlebox,1)
        new=button('+ Sınıf Oluştur'); new.clicked.connect(self.new_class); head.addWidget(new); delete=button('Sınıfı Sil',False); delete.clicked.connect(self.delete_class); head.addWidget(delete); root.addLayout(head)

        selector=QHBoxLayout(); selector.addWidget(QLabel('Aktif sınıf'))
        self.class_combo=QComboBox(); self.class_combo.currentIndexChanged.connect(self.load_class); selector.addWidget(self.class_combo,1)
        self.class_info=make_label('','accentText',True); selector.addWidget(self.class_info,2); root.addLayout(selector)

        plan_card,pl=card('Yeni Ders Planı')
        row1=QHBoxLayout(); row1.addWidget(QLabel('İşlenecek ders'))
        self.lesson_combo=QComboBox(); row1.addWidget(self.lesson_combo,2)
        row1.addWidget(QLabel('Tarih'))
        self.plan_date=QDateEdit(); self.plan_date.setCalendarPopup(True); self.plan_date.setDate(QDate.currentDate()); self.plan_date.setDisplayFormat('yyyy-MM-dd'); row1.addWidget(self.plan_date)
        pl.addLayout(row1)
        row2=QHBoxLayout(); self.plan_note=QLineEdit(); self.plan_note.setPlaceholderText('Ders notu / hedef (isteğe bağlı)'); row2.addWidget(self.plan_note,1); add=button('Ders Planına Ekle'); add.clicked.connect(self.add_plan); row2.addWidget(add); pl.addLayout(row2); root.addWidget(plan_card)

        root.addWidget(make_label('Ders Planı','cardTitle'))
        self.table=QTableWidget(0,6); self.table.setHorizontalHeaderLabels(['Tarih','Seviye','Ünite','Ders','Durum','Not']); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows); self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); self.table.verticalHeader().setVisible(False); root.addWidget(self.table,1)
        actions=QHBoxLayout(); done=button('✓ İşlendi Olarak İşaretle'); done.clicked.connect(lambda:self.set_status('İşlendi')); actions.addWidget(done); pending=button('↶ Bekliyor Yap',False); pending.clicked.connect(lambda:self.set_status('Bekliyor')); actions.addWidget(pending); remove=button('Planı Sil',False); remove.clicked.connect(self.delete_plan); actions.addWidget(remove); actions.addStretch(); close=button('Kapat',False); close.clicked.connect(self.accept); actions.addWidget(close); root.addLayout(actions)
        self.refresh_classes()
    def refresh_classes(self,select_id=None):
        rows=list(self.db.list_classes()); self.class_combo.blockSignals(True); self.class_combo.clear()
        for c in rows: self.class_combo.addItem(f"{c['name']}  •  {c['level_code']}  •  {c['done_count']}/{c['plan_count']} işlendi",c['id'])
        self.class_combo.blockSignals(False)
        if select_id is not None:
            idx=self.class_combo.findData(select_id); self.class_combo.setCurrentIndex(max(0,idx))
        if self.class_combo.count(): self.load_class()
        else:
            self.current_class_id=None; self.class_info.setText('Henüz sınıf oluşturulmadı.'); self.lesson_combo.clear(); self.table.setRowCount(0)
    def new_class(self):
        dlg=ClassCreateDialog(self.db,self)
        if dlg.exec()==QDialog.Accepted: self.refresh_classes(dlg.class_id)
    def delete_class(self):
        if not self.current_class_id: return
        cls=self.db.get_class(self.current_class_id)
        if QMessageBox.question(self,'Sınıfı Sil',f"'{cls['name']}' sınıfını ve tüm ders planını silmek istiyor musun?")!=QMessageBox.StandardButton.Yes: return
        self.db.delete_class(self.current_class_id); self.refresh_classes()
    def load_class(self):
        cid=self.class_combo.currentData(); self.current_class_id=cid
        if not cid: return
        cls=self.db.get_class(cid); self.class_info.setText(f"{cls['name']} • {cls['level_code']} • {cls['academic_year'] or 'Yıl belirtilmedi'}")
        self.lesson_combo.clear()
        for l in self.db.get_lessons(cls['level_code']): self.lesson_combo.addItem(f"Ünite {l['unit']} • {l['position']}. {l['title']}",l['id'])
        self.refresh_plans()
    def refresh_plans(self):
        self.plan_rows=list(self.db.list_class_plans(self.current_class_id)) if self.current_class_id else []; self.table.setRowCount(len(self.plan_rows))
        for r,p in enumerate(self.plan_rows):
            vals=[p['planned_date'] or 'Tarih yok',p['level_code'],p['unit'],p['lesson_title'],p['status'],p['notes'] or '—']
            for c,v in enumerate(vals): self.table.setItem(r,c,QTableWidgetItem(str(v)))
    def add_plan(self):
        if not self.current_class_id or not self.lesson_combo.currentData(): return
        self.db.add_class_plan(self.current_class_id,self.lesson_combo.currentData(),self.plan_date.date().toString('yyyy-MM-dd'),self.plan_note.text()); self.plan_note.clear(); self.refresh_classes(self.current_class_id); self.refresh_plans()
    def selected_plan(self):
        row=self.table.currentRow(); return self.plan_rows[row] if 0<=row<len(self.plan_rows) else None
    def set_status(self,status):
        p=self.selected_plan()
        if not p: return
        self.db.set_class_plan_status(p['id'],status); self.refresh_classes(self.current_class_id); self.refresh_plans()
    def delete_plan(self):
        p=self.selected_plan()
        if not p: return
        self.db.delete_class_plan(p['id']); self.refresh_classes(self.current_class_id); self.refresh_plans()


class MainWindow(QMainWindow):
    PAGE_TITLES={
        'dashboard':('Ana Sayfa','Kişisel öğrenme merkezin'),
        'levels':('Dersler','A1’den C2’ye öğrenme rotası'),
        'vocab':('Kelimeler','Kelime havuzun ve favorilerin'),
        'review':('Akıllı Tekrar','Bugün tekrar edilmesi gerekenler'),
        'listening':('Listening Lab','Dinleme becerini geliştir'),
        'speaking':('Speaking Studio','Sesli İngilizce pratiği'),
        'writing':('Writing Coach','Yazma becerini güçlendir'),
        'reading':('Reading Room','Okuma ve anlama pratiği'),
        'progress':('İlerleme','Performans ve öğrenme analitiği'),
        'achievements':('Başarımlar','Kilidini açtığın başarılar'),
        'settings':('Ayarlar','Profil ve uygulama tercihleri'),
        'lesson':('Ders Detayı','Odaklan • öğren • uygula'),
    }

    def __init__(self,db,app):
        super().__init__()
        self.db=db; self.app=app
        self.speech=SpeechService(db.get_profile()['tts_rate'])
        self.setWindowTitle('12/D Dil Programı — Teacher Premium Edition')
        self.resize(1440,900); self.setMinimumSize(1080,720)

        self.starfield=StarfieldWidget(theme=db.get_profile()['theme'], particle_count=135)
        self.setCentralWidget(self.starfield)
        root=QHBoxLayout(self.starfield); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        side=QFrame(); side.setObjectName('sidebar'); side.setFixedWidth(282)
        sl=QVBoxLayout(side); sl.setContentsMargins(16,18,16,16); sl.setSpacing(5)

        # Premium marka kartı:
        # Logo/title satırı, kredi alanı ve premium rozeti birbirinden
        # bağımsız tutulur. Böylece dar ekranda yazılar üst üste binmez.
        brand=QFrame(); brand.setObjectName('brandCard')
        brand.setMinimumHeight(148)
        brand.setMaximumHeight(148)

        bl=QVBoxLayout(brand)
        bl.setContentsMargins(14,12,14,11)
        bl.setSpacing(6)

        brow=QHBoxLayout()
        brow.setContentsMargins(0,0,0,0)
        brow.setSpacing(10)

        mark=QLabel('12/D')
        mark.setObjectName('logoMark')
        brow.addWidget(mark,0,Qt.AlignVCenter)

        btxt=QVBoxLayout()
        btxt.setContentsMargins(0,0,0,0)
        btxt.setSpacing(1)

        brand_title=make_label('DİL PROGRAMI','brandTitle')
        brand_sub=make_label('Premium English Hub','brandSub')
        brand_title.setMinimumHeight(20)
        brand_sub.setMinimumHeight(16)

        btxt.addStretch(1)
        btxt.addWidget(brand_title)
        btxt.addWidget(brand_sub)
        btxt.addStretch(1)

        brow.addLayout(btxt,1)
        bl.addLayout(brow)

        credit=QLabel('Made By Hacı Bozkurt\nThe Teacher Pelin Doğan Ortaç')
        credit.setObjectName('brandCredit')
        credit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        credit.setWordWrap(False)
        credit.setMinimumHeight(28)
        credit.setMaximumHeight(28)
        credit.setToolTip('Made By Hacı Bozkurt / The Teacher Pelin Doğan Ortaç')
        bl.addWidget(credit)

        tag=QLabel('✦  PREMIUM LEARNING')
        tag.setObjectName('premiumTag')
        tag.setAlignment(Qt.AlignCenter)
        tag.setMinimumHeight(24)
        tag.setMaximumHeight(24)
        bl.addWidget(tag)

        sl.addWidget(brand)
        sl.addSpacing(8)

        self.stack=QStackedWidget(); self.pages={}; self.nav_buttons={}
        groups=[
            ('GENEL',[
                ('dashboard','⌂   Ana Sayfa',lambda:DashboardPage(db,self)),
                ('levels','▦   Dersler',lambda:LevelsPage(db,self)),
                ('vocab','▤   Kelimeler',lambda:VocabularyPage(db,self)),
                ('review','↻   Akıllı Tekrar',lambda:ReviewPage(db)),
            ]),
            ('BECERİLER',[
                ('listening','▶   Listening',lambda:ListeningPage(db,self)),
                ('speaking','◉   Speaking',lambda:SpeakingPage(db,self)),
                ('reading','▣   Reading',lambda:ReadingPage(db)),
                ('writing','✎   Writing',lambda:WritingPage(db)),
            ]),
            ('GELİŞİM',[
                ('progress','◔   İlerleme',lambda:ProgressPage(db)),
                ('achievements','★   Başarımlar',lambda:AchievementsPage(db)),
            ]),
            ('SİSTEM',[
                ('settings','⚙   Ayarlar',lambda:SettingsPage(db,self,app)),
            ]),
        ]
        for section,items in groups:
            sec=QLabel(section); sec.setObjectName('navSection'); sl.addWidget(sec)
            for key,label,factory in items:
                page=factory(); self.pages[key]=page; self.stack.addWidget(page)
                b=QPushButton(label); b.setObjectName('navButton'); b.setProperty('active',False); b.setCursor(Qt.PointingHandCursor)
                b.clicked.connect(lambda _,k=key:self.open_page(k)); self.nav_buttons[key]=b; sl.addWidget(b)

        sl.addStretch()
        self.side_card=QFrame(); self.side_card.setObjectName('sideStatusCard')
        self.side_card.setMinimumHeight(132)
        scl=QVBoxLayout(self.side_card); scl.setContentsMargins(14,11,14,12); scl.setSpacing(4)
        current_caption=make_label('CURRENT LEVEL','sideCaption'); scl.addWidget(current_caption)
        self.side_level=make_label('A1','sideLevel'); scl.addWidget(self.side_level)
        self.side_progress_text=make_label('0 / 50 ders  •  %0','sideProgressText'); scl.addWidget(self.side_progress_text)
        self.side_progress=QProgressBar(); self.side_progress.setRange(0,100); self.side_progress.setTextVisible(False); self.side_progress.setFixedHeight(12); scl.addWidget(self.side_progress)
        self.side_note=make_label('','sideSmall',True); scl.addWidget(self.side_note)
        sl.addWidget(self.side_card)
        footer=make_label('Local-first • SQLite • 12/D','sideFooter',True); footer.setAlignment(Qt.AlignCenter); sl.addWidget(footer)

        main_shell=QFrame(); main_shell.setObjectName('mainShell')
        ml=QVBoxLayout(main_shell); ml.setContentsMargins(0,0,0,0); ml.setSpacing(0)
        top=QFrame(); top.setObjectName('topbar'); top.setFixedHeight(72)
        tl=QHBoxLayout(top); tl.setContentsMargins(30,12,28,12); tl.setSpacing(10)
        left=QVBoxLayout(); left.setSpacing(1); self.top_title=make_label('Ana Sayfa','topbarTitle'); self.top_sub=make_label('Kişisel öğrenme merkezin','topbarSub'); left.addWidget(self.top_title); left.addWidget(self.top_sub); tl.addLayout(left,1)
        self.level_pill=QLabel(); self.level_pill.setObjectName('levelPill'); tl.addWidget(self.level_pill)
        self.streak_pill=QLabel(); self.streak_pill.setObjectName('metricPill'); tl.addWidget(self.streak_pill)
        self.xp_pill=QLabel(); self.xp_pill.setObjectName('metricPill'); tl.addWidget(self.xp_pill)
        self.avatar=QLabel('Ö'); self.avatar.setObjectName('avatar'); tl.addWidget(self.avatar); self.menu_button=QPushButton('☰'); self.menu_button.setObjectName('menuButton'); self.menu_button.setCursor(Qt.PointingHandCursor); self.menu_button.setToolTip('Profil ve sınıf yönetimi'); self.menu_button.clicked.connect(self.show_hamburger_menu); tl.addWidget(self.menu_button)
        ml.addWidget(top); ml.addWidget(self.stack,1)

        root.addWidget(side); root.addWidget(main_shell,1)
        self.current_page_key='dashboard'
        self.shortcuts=[]; self.install_shortcuts()
        self.statusBar().showMessage('12/D Premium • Ctrl+1 Ana Sayfa • Ctrl+2 Dersler • Ctrl+R Tekrar • Ctrl+F Ara • F5 Yenile')
        self.open_page('dashboard')

    def show_hamburger_menu(self):
        p=self.db.get_profile(); menu=QMenu(self)
        who=menu.addAction(f"👤  {p['name']}  •  {p['role']}"); who.setEnabled(False)
        menu.addSeparator()
        menu.addAction('⇄  Profil Değiştir', self.open_profile_manager)
        menu.addAction('＋  Yeni Profil Oluştur', self.quick_create_profile)
        menu.addSeparator()
        menu.addAction('▦  Sınıf Yönetimi', self.open_class_manager)
        menu.addAction('＋  Sınıf Oluştur', self.quick_create_class)
        menu.addSeparator()
        menu.addAction('⚙  Ayarlar', lambda:self.open_page('settings'))
        pos=self.menu_button.mapToGlobal(self.menu_button.rect().bottomRight())
        menu.exec(pos)

    def apply_active_profile(self):
        p=self.db.get_profile(); apply_theme(self.app,p['theme']); self.starfield.set_theme(p['theme']); self.speech.rate=p['tts_rate']; self.refresh_all(); self.open_page('dashboard')

    def open_profile_manager(self):
        dlg=ProfileManagerDialog(self.db,self)
        dlg.exec()

        if not dlg.profile_changed:
            return

        # Son profil silindiyse ana uygulama profilsiz kullanılamaz.
        # MainWindow'u görünmez yap ve tekrar zorunlu profil kapısını aç.
        if not self.db.has_profiles():
            self.hide()

            create=ProfileCreateDialog(self.db,self,mandatory=True)
            result=create.exec()

            if result!=QDialog.DialogCode.Accepted or not self.db.has_profiles():
                QApplication.instance().quit()
                return

            self.apply_active_profile()
            self.show()
            self.raise_()
            self.activateWindow()
            return

        self.apply_active_profile()

    def quick_create_profile(self):
        dlg=ProfileCreateDialog(self.db,self)
        if dlg.exec()==QDialog.Accepted:
            self.db.switch_profile(dlg.created_profile_id); self.apply_active_profile()

    def open_class_manager(self):
        dlg=ClassManagerDialog(self.db,self); dlg.exec(); self.refresh_all()

    def quick_create_class(self):
        dlg=ClassCreateDialog(self.db,self)
        if dlg.exec()==QDialog.Accepted:
            manager=ClassManagerDialog(self.db,self); manager.refresh_classes(dlg.class_id); manager.exec(); self.refresh_all()

    def install_shortcuts(self):
        mapping=[('Ctrl+1','dashboard'),('Ctrl+2','levels'),('Ctrl+3','vocab'),('Ctrl+R','review')]
        for seq,key in mapping:
            sc=QShortcut(QKeySequence(seq),self); sc.activated.connect(lambda k=key:self.open_page(k)); self.shortcuts.append(sc)
        search=QShortcut(QKeySequence('Ctrl+F'),self); search.activated.connect(self.focus_lesson_search); self.shortcuts.append(search)
        refresh=QShortcut(QKeySequence('F5'),self); refresh.activated.connect(self.refresh_all); self.shortcuts.append(refresh)

    def focus_lesson_search(self):
        self.open_page('levels'); self.pages['levels'].focus_search()

    def run_first_setup_if_needed(self):
        # v2.3+ ilk profil kapısı MainWindow oluşturulmadan önce çalışır.
        return

    def refresh_topbar(self):
        p=self.db.get_profile(); title,sub=self.PAGE_TITLES.get(self.current_page_key,('12/D Dil Programı','Premium English Learning'))
        self.top_title.setText(title); self.top_sub.setText(sub)
        self.level_pill.setText(f"  {p['current_level']}  LEVEL  ")
        self.streak_pill.setText(f"🔥  {p['streak']} gün")
        self.xp_pill.setText(f"✦  {p['xp']} XP")
        name=(p['name'] or 'Öğrenci').strip(); self.avatar.setText(name[:1].upper() if name else 'Ö')
        self.avatar.setToolTip(f"{name} • {p['role']}")

    def refresh_sidebar(self):
        p=self.db.get_profile(); lp=self.db.current_level_progress()
        # The card always uses the real lesson count of the active CEFR level.
        # In v2.2+ this is 50 lessons per level, so legacy 10-lesson percentages
        # can no longer leak into the sidebar display.
        completed=int(lp.get('completed',0)); total=max(1,int(lp.get('total',0))); percent=round((completed/total)*100)
        self.side_level.setText(f"{p['current_level']}")
        self.side_progress_text.setText(f"{completed} / {total} ders  •  %{percent}")
        self.side_progress.setValue(percent)
        self.side_note.setText(f"🔥 {p['streak']} gün seri   •   ✦ {p['xp']} XP")
        self.refresh_topbar()

    def refresh_all(self):
        for p in self.pages.values():
            if hasattr(p,'refresh'):
                try: p.refresh()
                except Exception as e: print('Refresh warning:',type(p).__name__,e)
        self.refresh_sidebar()

    def open_page(self,key):
        p=self.pages[key]; self.current_page_key=key
        if hasattr(p,'refresh'):
            try: p.refresh()
            except Exception as e: print('Page refresh warning:',key,e)
        self.stack.setCurrentWidget(p)
        for k,b in self.nav_buttons.items():
            b.setProperty('active',k==key); b.style().unpolish(b); b.style().polish(b)
        self.refresh_sidebar()

    def open_lesson(self,lesson_id):
        if not self.db.lesson_accessible(lesson_id): QMessageBox.warning(self,'Kilitli','Önce önceki dersi tamamlamalısın.'); return
        page=LessonPage(self.db,self,lesson_id); self.stack.addWidget(page); self.stack.setCurrentWidget(page)
        self.current_page_key='lesson'
        for b in self.nav_buttons.values(): b.setProperty('active',False); b.style().unpolish(b); b.style().polish(b)
        self.refresh_sidebar()

    def speak(self,text):
        ok,msg=self.speech.speak(text)
        if not ok: QMessageBox.information(self,'Seslendirme',msg)
