import json
import math
import random
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from mobile_app.database import Database, LEVEL_ORDER

APP_NAME = "12/D Dil Programı"
CREDIT = "Made By Hacı Bozkurt / The Teacher Pelin Doğan Ortaç"

COLORS = {
    "bg": (0.025, 0.04, 0.075, 1),
    "panel": (0.055, 0.075, 0.13, 0.96),
    "panel2": (0.075, 0.10, 0.17, 0.97),
    "border": (0.22, 0.28, 0.45, 1),
    "primary": (0.40, 0.50, 0.95, 1),
    "primary2": (0.52, 0.39, 0.95, 1),
    "cyan": (0.32, 0.84, 0.96, 1),
    "text": (0.95, 0.97, 1, 1),
    "muted": (0.62, 0.67, 0.77, 1),
    "danger": (0.92, 0.30, 0.36, 1),
    "good": (0.26, 0.78, 0.52, 1),
}


def rgba(hex_value, alpha=1.0):
    h = hex_value.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4)) + (alpha,)


class Starfield(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stars = []
        for _ in range(80):
            self.stars.append([
                random.random(), random.random(),
                random.uniform(0.7, 2.1),
                random.uniform(0.0006, 0.0018),
                random.uniform(0.25, 1.0),
            ])
        Clock.schedule_interval(self.tick, 1/30)

    def tick(self, dt):
        if not self.parent:
            return
        for s in self.stars:
            s[1] += s[3] * (1 + s[4])
            if s[1] > 1.02:
                s[0] = random.random()
                s[1] = -0.02
        self.canvas.clear()
        with self.canvas:
            Color(*COLORS["bg"])
            Rectangle(pos=self.pos, size=self.size)
            for x, y, size, speed, depth in self.stars:
                Color(0.55, 0.70, 1.0, 0.18 + 0.50 * depth)
                Ellipse(
                    pos=(self.x + x*self.width, self.y + y*self.height),
                    size=(dp(size), dp(size))
                )


class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = dp(14)
        self.spacing = dp(8)
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def _redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLORS["panel"])
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
            Color(*COLORS["border"])
            # subtle top border
            Rectangle(pos=(self.x, self.top-dp(1)), size=(self.width, dp(1)))


class PrimaryButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", COLORS["primary"])
        kwargs.setdefault("color", COLORS["text"])
        kwargs.setdefault("font_size", sp(14))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(48))
        super().__init__(**kwargs)


class SoftButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", COLORS["panel2"])
        kwargs.setdefault("color", COLORS["text"])
        kwargs.setdefault("font_size", sp(13))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(46))
        super().__init__(**kwargs)


def title(text, size=26):
    return Label(
        text=text, color=COLORS["text"], font_size=sp(size),
        bold=True, size_hint_y=None, height=dp(size + 20),
        halign="left", valign="middle"
    )


def muted(text, height=44):
    l = Label(
        text=text, color=COLORS["muted"], font_size=sp(12),
        size_hint_y=None, height=dp(height), halign="left", valign="top"
    )
    l.bind(size=lambda inst, val: setattr(inst, "text_size", (inst.width, None)))
    return l


class Header(BoxLayout):
    def __init__(self, screen_title, app, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(64), spacing=dp(8), **kwargs)
        back = SoftButton(text="‹", size_hint_x=None, width=dp(52))
        back.bind(on_release=lambda *_: app.go_home())
        self.add_widget(back)
        lab = Label(text=screen_title, bold=True, font_size=sp(18), color=COLORS["text"], halign="left")
        lab.bind(size=lambda inst, val: setattr(inst, "text_size", inst.size))
        self.add_widget(lab)
        menu = SoftButton(text="☰", size_hint_x=None, width=dp(52))
        menu.bind(on_release=lambda *_: app.show_profile_menu())
        self.add_widget(menu)


class DashboardScreen(Screen):
    def on_pre_enter(self, *args):
        self.clear_widgets()
        app = App.get_running_app()

        root = BoxLayout(orientation="vertical")
        bg = Starfield()
        root.add_widget(bg)

        overlay = BoxLayout(orientation="vertical", padding=[dp(16), dp(18), dp(16), dp(12)], spacing=dp(12))
        bg.add_widget(overlay)

        top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(62))
        brand = BoxLayout(orientation="vertical")
        brand.add_widget(Label(text="12/D DİL PROGRAMI", bold=True, font_size=sp(18), color=COLORS["text"], halign="left"))
        brand.add_widget(Label(text="Premium English Hub", font_size=sp(10), color=COLORS["cyan"], halign="left"))
        top.add_widget(brand)
        menu = SoftButton(text="☰", size_hint_x=None, width=dp(52))
        menu.bind(on_release=lambda *_: app.show_profile_menu())
        top.add_widget(menu)
        overlay.add_widget(top)

        profile = app.db.get_profile()
        if not profile:
            Clock.schedule_once(lambda dt: app.ensure_profile(), 0)
            return

        overlay.add_widget(title(f"Merhaba, {profile['name']} 👋", 25))
        overlay.add_widget(muted("Bugünkü çalışma rotan hazır. Kaldığın yerden devam edebilirsin.", 34))

        stats = app.db.stats()
        cur = app.db.current_level_progress()

        stat_row = BoxLayout(size_hint_y=None, height=dp(92), spacing=dp(8))
        for value, label_text in [
            (profile["current_level"], "SEVİYE"),
            (str(profile["xp"]), "XP"),
            (f"{profile['streak']} gün", "SERİ"),
        ]:
            c = Card(orientation="vertical")
            c.add_widget(Label(text=str(value), bold=True, font_size=sp(21), color=COLORS["text"]))
            c.add_widget(Label(text=label_text, font_size=sp(9), color=COLORS["muted"]))
            stat_row.add_widget(c)
        overlay.add_widget(stat_row)

        hero = Card(orientation="vertical", size_hint_y=None, height=dp(178))
        hero.add_widget(Label(text="✦ PREMIUM LEARNING PATH", bold=True, font_size=sp(11), color=COLORS["cyan"], halign="left"))
        next_lesson = app.db.next_lesson()
        if next_lesson:
            hero.add_widget(Label(
                text=f"{next_lesson['level_code']} • Ders {next_lesson['position']}\n{next_lesson['title']}",
                bold=True, font_size=sp(18), color=COLORS["text"], halign="left"
            ))
            b = PrimaryButton(text="Derse Devam Et →")
            b.bind(on_release=lambda *_: app.open_lesson(next_lesson["id"]))
            hero.add_widget(b)
        else:
            hero.add_widget(Label(text="Tüm erişilebilir dersler tamamlandı.", color=COLORS["text"]))
        overlay.add_widget(hero)

        progress_card = Card(orientation="vertical", size_hint_y=None, height=dp(120))
        progress_card.add_widget(Label(
            text=f"{profile['current_level']} ilerlemesi  •  {cur['completed']} / {cur['total']} ders",
            bold=True, color=COLORS["text"], halign="left"
        ))
        pb = ProgressBar(max=100, value=cur["percent"], size_hint_y=None, height=dp(16))
        progress_card.add_widget(pb)
        progress_card.add_widget(Label(text=f"%{cur['percent']} tamamlandı", color=COLORS["muted"], font_size=sp(11)))
        overlay.add_widget(progress_card)

        nav = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(6))
        for txt, screen in [("⌂ Ana", "home"), ("▦ Dersler", "lessons"), ("★ Kelime", "words"), ("▣ Sınıf", "classes")]:
            b = SoftButton(text=txt)
            b.bind(on_release=lambda inst, s=screen: app.go(s))
            nav.add_widget(b)
        overlay.add_widget(nav)


class LessonsScreen(Screen):
    selected_level = StringProperty("A1")

    def on_pre_enter(self, *args):
        self.render()

    def render(self):
        self.clear_widgets()
        app = App.get_running_app()
        root = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        root.add_widget(Header("Dersler", app))

        profile = app.db.get_profile()
        self.selected_level = profile["current_level"] if profile else "A1"

        spinner = Spinner(
            text=self.selected_level, values=LEVEL_ORDER,
            size_hint_y=None, height=dp(48),
            background_normal="", background_color=COLORS["panel2"], color=COLORS["text"]
        )
        spinner.bind(text=self._change_level)
        root.add_widget(spinner)

        self.lesson_scroll = ScrollView()
        self.lesson_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=[0, 0, 0, dp(20)])
        self.lesson_box.bind(minimum_height=self.lesson_box.setter("height"))
        self.lesson_scroll.add_widget(self.lesson_box)
        root.add_widget(self.lesson_scroll)
        self.add_widget(root)
        self.load_lessons(self.selected_level)

    def _change_level(self, spinner, text):
        self.selected_level = text
        self.load_lessons(text)

    def load_lessons(self, level):
        app = App.get_running_app()
        self.lesson_box.clear_widgets()
        accessible_level = app.db.level_accessible(level)
        lessons = app.db.get_lessons(level)

        if not accessible_level:
            lock = Card(orientation="vertical", size_hint_y=None, height=dp(110))
            lock.add_widget(Label(text="🔒 Bu seviye henüz kilitli.", bold=True, color=COLORS["text"]))
            lock.add_widget(Label(text="Önce önceki seviyeyi tamamla.", color=COLORS["muted"]))
            self.lesson_box.add_widget(lock)
            return

        for lesson in lessons:
            card = Card(orientation="horizontal", size_hint_y=None, height=dp(90), spacing=dp(10))
            status = "✓" if lesson["completed"] else ("▶" if app.db.lesson_accessible(lesson["id"]) else "🔒")
            status_lab = Label(text=status, size_hint_x=None, width=dp(38), bold=True, font_size=sp(18), color=COLORS["cyan"])
            card.add_widget(status_lab)

            info = BoxLayout(orientation="vertical")
            info.add_widget(Label(
                text=f"{lesson['position']}. {lesson['title']}",
                bold=True, color=COLORS["text"], halign="left", valign="middle"
            ))
            info.add_widget(Label(
                text=f"Ünite {lesson['unit']} • En iyi skor %{lesson['best_score']}",
                color=COLORS["muted"], font_size=sp(10), halign="left"
            ))
            card.add_widget(info)

            btn = SoftButton(text="Aç", size_hint_x=None, width=dp(70))
            can = app.db.lesson_accessible(lesson["id"])
            btn.disabled = not can
            if can:
                btn.bind(on_release=lambda inst, lid=lesson["id"]: app.open_lesson(lid))
            card.add_widget(btn)
            self.lesson_box.add_widget(card)


class LessonScreen(Screen):
    lesson_id = NumericProperty(0)

    def show_lesson(self, lesson_id):
        self.lesson_id = lesson_id
        self.render()

    def render(self):
        self.clear_widgets()
        app = App.get_running_app()
        lesson = app.db.get_lesson(self.lesson_id)
        if not lesson:
            app.go("lessons")
            return

        root = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        root.add_widget(Header(f"{lesson['level_code']} • Ders {lesson['position']}", app))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10), padding=[0, 0, 0, dp(30)])
        content.bind(minimum_height=content.setter("height"))

        heading = Card(orientation="vertical", size_hint_y=None, height=dp(150))
        heading.add_widget(Label(text=lesson["title"], bold=True, font_size=sp(22), color=COLORS["text"]))
        heading.add_widget(Label(text=lesson["description"], color=COLORS["muted"], font_size=sp(11)))
        heading.add_widget(Label(text=f"Grammar: {lesson['grammar']}", color=COLORS["cyan"], font_size=sp(11)))
        content.add_widget(heading)

        for label_text, body in [
            ("KELİMELER", lesson["vocabulary"].replace(";", "\n").replace("|", "  →  ")),
            ("ÖRNEK", lesson["example"].replace("|", "\n")),
            ("READING", lesson["reading_text"]),
            ("LISTENING", lesson["listening_text"]),
            ("SPEAKING", lesson["speaking_prompt"]),
            ("WRITING", lesson["writing_prompt"]),
        ]:
            c = Card(orientation="vertical", size_hint_y=None)
            lines = max(2, body.count("\n") + 2)
            c.height = dp(52 + min(220, lines * 22))
            c.add_widget(Label(text=label_text, bold=True, color=COLORS["cyan"], font_size=sp(10), halign="left"))
            l = Label(text=body, color=COLORS["text"], font_size=sp(12), halign="left", valign="top")
            l.bind(size=lambda inst, val: setattr(inst, "text_size", (inst.width, None)))
            c.add_widget(l)
            if label_text == "LISTENING":
                speak = SoftButton(text="🔊 Dinle")
                speak.bind(on_release=lambda *_args, txt=lesson["listening_text"]: app.speak_text(txt))
                c.add_widget(speak)
                c.height += dp(52)
            content.add_widget(c)

        quiz = json.loads(lesson["quiz"])
        qcard = Card(orientation="vertical", size_hint_y=None, height=dp(360))
        qcard.add_widget(Label(text="MİNİ QUIZ", bold=True, color=COLORS["cyan"], font_size=sp(11)))
        first = quiz[0]
        qcard.add_widget(Label(text=first["question"], color=COLORS["text"], font_size=sp(14), halign="left"))
        for idx, option in enumerate(first["options"]):
            b = SoftButton(text=option)
            b.bind(on_release=lambda inst, i=idx, correct=first["correct"]: self.answer(i, correct))
            qcard.add_widget(b)
        content.add_widget(qcard)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def answer(self, selected, correct):
        app = App.get_running_app()
        if selected == correct:
            earned = app.db.complete_lesson(self.lesson_id, 100)
            app.toast(f"Doğru! +{earned} XP")
            Clock.schedule_once(lambda dt: app.go("lessons"), 0.8)
        else:
            app.toast("Yanlış cevap. Tekrar deneyebilirsin.")


class WordsScreen(Screen):
    def on_pre_enter(self, *args):
        self.render()

    def render(self):
        self.clear_widgets()
        app = App.get_running_app()
        root = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        root.add_widget(Header("Kelime Merkezi", app))

        due = app.db.due_words(50)
        root.add_widget(Label(
            text=f"Bugün tekrar bekleyen: {len(due)}",
            size_hint_y=None, height=dp(36), color=COLORS["cyan"], bold=True
        ))

        scroll = ScrollView()
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=[0,0,0,dp(25)])
        box.bind(minimum_height=box.setter("height"))

        words = due if due else app.db.all_words()[:50]
        if not words:
            c = Card(orientation="vertical", size_hint_y=None, height=dp(120))
            c.add_widget(Label(text="Henüz kelime yok.", bold=True, color=COLORS["text"]))
            c.add_widget(Label(text="Ders tamamladıkça kelimeler buraya eklenir.", color=COLORS["muted"]))
            box.add_widget(c)

        for w in words:
            c = Card(orientation="vertical", size_hint_y=None, height=dp(150))
            c.add_widget(Label(text=w["word"], bold=True, font_size=sp(18), color=COLORS["text"]))
            c.add_widget(Label(text=w["translation"], color=COLORS["cyan"], font_size=sp(12)))
            c.add_widget(Label(text=w["example"] or "", color=COLORS["muted"], font_size=sp(10)))
            row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(5))
            for txt, quality in [("Zor", 2), ("Orta", 3), ("Kolay", 5)]:
                b = SoftButton(text=txt)
                b.bind(on_release=lambda inst, wid=w["id"], q=quality: self.review(wid, q))
                row.add_widget(b)
            c.add_widget(row)
            box.add_widget(c)

        scroll.add_widget(box)
        root.add_widget(scroll)
        self.add_widget(root)

    def review(self, word_id, quality):
        app = App.get_running_app()
        app.db.review_word(word_id, quality)
        app.toast("Tekrar kaydedildi.")
        self.render()


class ClassesScreen(Screen):
    def on_pre_enter(self, *args):
        self.render()

    def render(self):
        self.clear_widgets()
        app = App.get_running_app()
        root = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        root.add_widget(Header("Sınıflar", app))

        profile = app.db.get_profile()
        if not profile or profile["role"] != "Öğretmen":
            c = Card(orientation="vertical", size_hint_y=None, height=dp(120))
            c.add_widget(Label(text="Sınıf yönetimi öğretmen profillerine özeldir.", color=COLORS["text"], bold=True))
            root.add_widget(c)
            self.add_widget(root)
            return

        new_btn = PrimaryButton(text="+ Yeni Sınıf")
        new_btn.bind(on_release=lambda *_: app.create_class_popup(self))
        root.add_widget(new_btn)

        scroll = ScrollView()
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=[0,0,0,dp(20)])
        box.bind(minimum_height=box.setter("height"))

        classes = app.db.list_classes()
        if not classes:
            c = Card(orientation="vertical", size_hint_y=None, height=dp(110))
            c.add_widget(Label(text="Henüz sınıf yok.", color=COLORS["text"], bold=True))
            c.add_widget(Label(text="+ Yeni Sınıf ile ilk sınıfını oluştur.", color=COLORS["muted"]))
            box.add_widget(c)

        for cls in classes:
            c = Card(orientation="vertical", size_hint_y=None)
            plans = app.db.list_class_plans(cls["id"])
            c.height = dp(120 + min(4, len(plans))*56)
            c.add_widget(Label(
                text=f"{cls['name']}  •  {cls['level_code']}  •  {cls['academic_year']}",
                bold=True, color=COLORS["text"], font_size=sp(16)
            ))
            if plans:
                for p in plans[:4]:
                    c.add_widget(Label(
                        text=f"{'✓' if p['status']=='İşlendi' else '○'} {p['planned_date']} • {p['lesson_title']}",
                        color=COLORS["good"] if p["status"]=="İşlendi" else COLORS["muted"],
                        font_size=sp(10), halign="left"
                    ))
            else:
                c.add_widget(Label(text="Henüz ders planı eklenmemiş.", color=COLORS["muted"], font_size=sp(10)))
            b = SoftButton(text="Ders Planı Ekle")
            b.bind(on_release=lambda inst, cid=cls["id"]: app.class_plan_popup(cid, self))
            c.add_widget(b)
            box.add_widget(c)

        scroll.add_widget(box)
        root.add_widget(scroll)
        self.add_widget(root)


class ProfileScreen(Screen):
    def on_pre_enter(self, *args):
        self.render()

    def render(self):
        self.clear_widgets()
        app = App.get_running_app()
        root = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        root.add_widget(Header("Profiller", app))

        new_btn = PrimaryButton(text="+ Yeni Profil")
        new_btn.bind(on_release=lambda *_: app.profile_popup())
        root.add_widget(new_btn)

        scroll = ScrollView()
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        box.bind(minimum_height=box.setter("height"))

        for p in app.db.list_profiles():
            c = Card(orientation="horizontal", size_hint_y=None, height=dp(86), spacing=dp(8))
            label = Label(
                text=f"{'● ' if p['active'] else ''}{p['name']}\n{p['role']} • {p['current_level']} • {p['xp']} XP",
                color=COLORS["text"], halign="left", valign="middle", font_size=sp(12)
            )
            label.bind(size=lambda inst, val: setattr(inst, "text_size", inst.size))
            c.add_widget(label)
            switch = SoftButton(text="Seç", size_hint_x=None, width=dp(65))
            switch.bind(on_release=lambda inst, pid=p["id"]: self.switch(pid))
            c.add_widget(switch)
            delete = SoftButton(text="Sil", size_hint_x=None, width=dp(60), background_color=COLORS["danger"])
            delete.bind(on_release=lambda inst, pid=p["id"], name=p["name"]: app.delete_profile_confirm(pid, name))
            c.add_widget(delete)
            box.add_widget(c)

        scroll.add_widget(box)
        root.add_widget(scroll)
        self.add_widget(root)

    def switch(self, pid):
        app = App.get_running_app()
        app.db.switch_profile(pid)
        app.toast("Profil değiştirildi.")
        app.go("home")


class Native12DApp(App):
    def build(self):
        Window.clearcolor = COLORS["bg"]
        self.title = APP_NAME

        db_path = Path(self.user_data_dir) / "12d_dil_programi.db"
        self.db = Database(db_path)
        self.db.initialize()

        self.sm = ScreenManager(transition=SlideTransition(duration=0.18))
        self.sm.add_widget(DashboardScreen(name="home"))
        self.sm.add_widget(LessonsScreen(name="lessons"))
        self.sm.add_widget(LessonScreen(name="lesson"))
        self.sm.add_widget(WordsScreen(name="words"))
        self.sm.add_widget(ClassesScreen(name="classes"))
        self.sm.add_widget(ProfileScreen(name="profiles"))

        Clock.schedule_once(lambda dt: self.ensure_profile(), 0.25)
        return self.sm

    def ensure_profile(self):
        if self.db.has_profiles():
            self.go("home")
            return
        self.profile_popup(mandatory=True)

    def go(self, name):
        if not self.db.has_profiles() and name != "profiles":
            self.ensure_profile()
            return
        self.sm.current = name

    def go_home(self):
        self.go("home")

    def open_lesson(self, lesson_id):
        screen = self.sm.get_screen("lesson")
        screen.show_lesson(lesson_id)
        self.sm.current = "lesson"

    def toast(self, message):
        view = ModalView(size_hint=(0.84, None), height=dp(64), background_color=(0,0,0,0))
        card = Card()
        card.add_widget(Label(text=message, color=COLORS["text"], bold=True))
        view.add_widget(card)
        view.open()
        Clock.schedule_once(lambda dt: view.dismiss(), 1.3)

    def show_profile_menu(self):
        self.go("profiles")

    def profile_popup(self, mandatory=False):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        content.add_widget(Label(
            text="İlk profilini oluştur" if mandatory else "Yeni Profil",
            bold=True, font_size=sp(20), color=COLORS["text"], size_hint_y=None, height=dp(42)
        ))
        if mandatory:
            content.add_widget(muted("Profil oluşturmadan uygulamaya erişilemez.", 35))

        name = TextInput(
            hint_text="Profil adı", multiline=False, size_hint_y=None, height=dp(46),
            background_color=COLORS["panel2"], foreground_color=COLORS["text"],
            hint_text_color=COLORS["muted"]
        )
        role = Spinner(
            text="Öğretmen", values=("Öğretmen", "Öğrenci"),
            size_hint_y=None, height=dp(46), background_normal="",
            background_color=COLORS["panel2"], color=COLORS["text"]
        )
        level = Spinner(
            text="A1", values=tuple(LEVEL_ORDER),
            size_hint_y=None, height=dp(46), background_normal="",
            background_color=COLORS["panel2"], color=COLORS["text"]
        )
        content.add_widget(name)
        content.add_widget(role)
        content.add_widget(level)

        buttons = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        if not mandatory:
            cancel = SoftButton(text="Vazgeç")
            buttons.add_widget(cancel)
        save = PrimaryButton(text="Profili Oluştur")
        buttons.add_widget(save)
        content.add_widget(buttons)

        popup = Popup(
            title="", content=content, size_hint=(0.92, None), height=dp(390),
            auto_dismiss=not mandatory, background=""
        )
        if not mandatory:
            cancel.bind(on_release=lambda *_: popup.dismiss())

        def create(*_):
            try:
                pid = self.db.create_profile(name.text, role.text, level.text, 20)
                self.db.switch_profile(pid)
            except Exception as exc:
                self.toast(str(exc))
                return
            popup.dismiss()
            self.go("home")

        save.bind(on_release=create)
        popup.open()

    def delete_profile_confirm(self, pid, profile_name):
        content = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))
        content.add_widget(Label(
            text="Bu profili silmek istediğinize emin misiniz?",
            bold=True, color=COLORS["text"], font_size=sp(16)
        ))
        content.add_widget(muted(f"Profil: {profile_name}\nBu profile ait ilerleme verileri de silinecek.", 68))
        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        no = SoftButton(text="Hayır")
        yes = PrimaryButton(text="Evet, Profili Sil", background_color=COLORS["danger"])
        row.add_widget(no)
        row.add_widget(yes)
        content.add_widget(row)
        pop = Popup(title="", content=content, size_hint=(0.92, None), height=dp(255), background="")
        no.bind(on_release=lambda *_: pop.dismiss())

        def delete(*_):
            remain = self.db.delete_profile(pid)
            pop.dismiss()
            if not remain:
                self.profile_popup(mandatory=True)
            else:
                self.sm.get_screen("profiles").render()
        yes.bind(on_release=delete)
        pop.open()

    def create_class_popup(self, screen):
        content = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(9))
        name = TextInput(hint_text="Sınıf adı (örn. 12/D)", multiline=False, size_hint_y=None, height=dp(45))
        level = Spinner(text="A1", values=tuple(LEVEL_ORDER), size_hint_y=None, height=dp(45))
        year = TextInput(hint_text="Eğitim yılı (örn. 2026-2027)", multiline=False, size_hint_y=None, height=dp(45))
        content.add_widget(name); content.add_widget(level); content.add_widget(year)
        save = PrimaryButton(text="Sınıfı Oluştur")
        content.add_widget(save)
        pop = Popup(title="Yeni Sınıf", content=content, size_hint=(0.92, None), height=dp(330))
        def create(*_):
            try:
                self.db.create_class(name.text, level.text, year.text, "")
            except Exception as exc:
                self.toast(str(exc)); return
            pop.dismiss(); screen.render()
        save.bind(on_release=create)
        pop.open()

    def class_plan_popup(self, class_id, screen):
        cls = self.db.get_class(class_id)
        lessons = self.db.get_lessons(cls["level_code"])
        values = tuple(f"{l['position']}. {l['title']}" for l in lessons)
        mapping = {f"{l['position']}. {l['title']}": l["id"] for l in lessons}

        content = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(9))
        lesson = Spinner(text=values[0] if values else "Ders yok", values=values, size_hint_y=None, height=dp(46))
        date_input = TextInput(hint_text="Tarih: YYYY-MM-DD", multiline=False, size_hint_y=None, height=dp(45))
        note = TextInput(hint_text="Öğretmen notu", multiline=True, size_hint_y=None, height=dp(90))
        content.add_widget(lesson); content.add_widget(date_input); content.add_widget(note)
        save = PrimaryButton(text="Ders Planını Ekle")
        content.add_widget(save)
        pop = Popup(title=f"{cls['name']} • Ders Planı", content=content, size_hint=(0.94, None), height=dp(410))
        def add(*_):
            if not values:
                return
            self.db.add_class_plan(class_id, mapping[lesson.text], date_input.text, note.text)
            pop.dismiss(); screen.render()
        save.bind(on_release=add)
        pop.open()

    def speak_text(self, text):
        # Native Android TTS. Desktop debug runs simply show a message.
        try:
            from plyer import tts
            tts.speak(text)
        except Exception:
            self.toast("Seslendirme Android cihazda kullanılabilir.")


if __name__ == "__main__":
    Native12DApp().run()
