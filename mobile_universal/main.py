import json
import random
import traceback
import unicodedata
from datetime import date
from pathlib import Path

from kivy.app import App
from kivy.base import ExceptionHandler, ExceptionManager
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget

from mobile_app.curriculum import PLACEMENT_QUESTIONS
from mobile_app.database import Database, LEVEL_ORDER
from mobile_app.services import speaking_score, writing_score
from mobile_app.platform_services import MobileSpeech, configure_mobile_text_environment

APP_NAME = '12/D Dil Programı'
CREDIT = 'Made By Hacı Bozkurt / The Teacher Pelin Doğan Ortaç'

THEMES = {
    'dark': {
        'bg': (0.025, 0.04, 0.075, 1), 'panel': (0.055, 0.075, 0.13, .98),
        'panel2': (0.075, 0.10, 0.17, 1), 'line': (0.22, 0.28, 0.45, 1),
        'primary': (0.40, 0.50, 0.95, 1), 'text': (0.95, 0.97, 1, 1),
        'muted': (0.62, 0.67, 0.77, 1), 'cyan': (0.32, 0.84, 0.96, 1),
        'danger': (0.92, 0.30, 0.36, 1), 'good': (0.26, 0.78, 0.52, 1),
    },
    'light': {
        'bg': (0.95, 0.965, 0.99, 1), 'panel': (1, 1, 1, .99),
        'panel2': (0.92, 0.94, 0.98, 1), 'line': (0.72, 0.76, 0.85, 1),
        'primary': (0.34, 0.40, 0.88, 1), 'text': (0.08, 0.11, 0.18, 1),
        'muted': (0.38, 0.43, 0.54, 1), 'cyan': (0.06, 0.52, 0.72, 1),
        'danger': (0.82, 0.20, 0.28, 1), 'good': (0.12, 0.58, 0.34, 1),
    },
}


def C(key):
    app = App.get_running_app()
    theme = getattr(app, 'theme_name', 'dark') if app else 'dark'
    return THEMES.get(theme, THEMES['dark'])[key]


def normalize_mobile_text(value):
    """Normalize Android/iOS keyboard text for Turkish characters."""
    text = unicodedata.normalize('NFC', str(value or ''))
    # Broken IMEs / locale conversions can leave an extra combining dot.
    for broken, fixed in (
        ('İ\u0307', 'İ'), ('I\u0307', 'İ'),
        ('i\u0307', 'i'), ('ı\u0307', 'ı'),
    ):
        text = text.replace(broken, fixed)
    text = text.replace('\u200b', '').replace('\ufeff', '').replace('\u2060', '')
    return unicodedata.normalize('NFC', text)


def turkish_lower(value):
    text = normalize_mobile_text(value)
    return normalize_mobile_text(text.replace('I', 'ı').replace('İ', 'i').lower())


def turkish_upper(value):
    text = normalize_mobile_text(value)
    return normalize_mobile_text(text.replace('i', 'İ').replace('ı', 'I').upper())


class TurkishTextInput(TextInput):
    """TextInput that uses the app's own Turkish Q keyboard on Android/iOS."""
    def __init__(self, **kwargs):
        kwargs.setdefault('input_type', 'text')
        kwargs.setdefault('write_tab', False)
        kwargs.setdefault('keyboard_suggestions', False)
        kwargs.setdefault('font_name', 'Roboto')
        # managed prevents Android/iOS from automatically opening the English
        # system keyboard. The app's Turkish Q keyboard is shown instead.
        kwargs.setdefault('keyboard_mode', 'managed')
        super().__init__(**kwargs)
        self._normalizing_tr_text = False
        self.bind(text=self._normalize_whole_value)
        self.bind(focus=self._turkish_keyboard_focus)

    def _turkish_keyboard_focus(self, inst, focused):
        if not focused:
            return
        app = App.get_running_app()
        if app and hasattr(app, 'show_turkish_keyboard'):
            Clock.schedule_once(lambda dt: app.show_turkish_keyboard(self), 0)

    def insert_text(self, substring, from_undo=False):
        incoming = normalize_mobile_text(substring)
        if incoming == '\u0307':
            idx = self.cursor_index()
            if idx > 0 and self.text[idx - 1:idx] in ('i', 'ı', 'I', 'İ'):
                return
        return super().insert_text(incoming, from_undo=from_undo)

    def _normalize_whole_value(self, inst, value):
        if self._normalizing_tr_text:
            return
        cleaned = normalize_mobile_text(value)
        if cleaned == value:
            return
        try:
            old_index = self.cursor_index()
            self._normalizing_tr_text = True
            self.text = cleaned
            self.cursor = self.get_cursor_from_index(min(old_index, len(cleaned)))
        finally:
            self._normalizing_tr_text = False


def safe_json_list(value):
    """Return a JSON list without ever crashing a mobile screen."""
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value or '[]')
        return parsed if isinstance(parsed, list) else []
    except (TypeError, ValueError, json.JSONDecodeError):
        return []


def fit_label(label):
    """Constrain text and normalize Turkish/mobile Unicode."""
    label.text = normalize_mobile_text(label.text)
    def _fit(inst, *_):
        inst.text_size = (max(dp(8), inst.width), max(dp(8), inst.height))
    def _clean_text(inst, value):
        cleaned = normalize_mobile_text(value)
        if cleaned != value:
            inst.text = cleaned
    label.bind(size=_fit, text=_clean_text)
    Clock.schedule_once(lambda dt: _fit(label), 0)
    return label


def auto_label(text, size=12, bold=False, color_key='text', min_height=28,
               halign='left'):
    """Wrapped label whose height follows its real text texture."""
    lab = Label(
        text=normalize_mobile_text(text), font_name='Roboto', bold=bold, font_size=sp(size), color=C(color_key),
        size_hint_y=None, halign=halign, valign='top'
    )
    def _width(inst, *_):
        inst.text_size = (max(dp(24), inst.width), None)
    def _texture(inst, value):
        inst.height = max(dp(min_height), value[1] + dp(8))
    lab.bind(width=_width, texture_size=_texture)
    Clock.schedule_once(lambda dt: _width(lab), 0)
    return lab


def heading(text, size=24, height=56):
    return fit_label(Label(text=normalize_mobile_text(text), font_name='Roboto', bold=True, font_size=sp(size), color=C('text'),
                           size_hint_y=None, height=dp(height), halign='left', valign='middle'))


def muted(text, height=44):
    return fit_label(Label(text=normalize_mobile_text(text), font_name='Roboto', font_size=sp(11), color=C('muted'),
                           size_hint_y=None, height=dp(height), halign='left', valign='top'))


def field(hint='', multiline=False, height=48):
    return TurkishTextInput(
        hint_text=normalize_mobile_text(hint), multiline=multiline,
        size_hint_y=None, height=dp(height), input_type='text',
        keyboard_suggestions=False, write_tab=False, font_name='Roboto',
        keyboard_mode='managed',
        background_color=C('panel2'), foreground_color=C('text'),
        hint_text_color=C('muted'), padding=[dp(12), dp(12)],
        font_size=sp(13)
    )


class Starfield(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stars = [[random.random(), random.random(), random.uniform(.7, 2.0), random.uniform(.0005, .0015), random.random()] for _ in range(70)]
        Clock.schedule_interval(self.tick, 1/30)

    def tick(self, dt):
        if not self.parent:
            return
        for s in self.stars:
            s[1] += s[3]
            if s[1] > 1.02:
                s[0], s[1] = random.random(), -.02
        self.canvas.clear()
        with self.canvas:
            Color(*C('bg')); Rectangle(pos=self.pos, size=self.size)
            for x, y, size, speed, depth in self.stars:
                if App.get_running_app().theme_name == 'light':
                    Color(.25, .35, .65, .10 + .18*depth)
                else:
                    Color(.55, .70, 1, .18 + .48*depth)
                Ellipse(pos=(self.x+x*self.width, self.y+y*self.height), size=(dp(size), dp(size)))


class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = kwargs.get('padding', dp(14))
        self.spacing = kwargs.get('spacing', dp(8))
        self.bind(pos=self.redraw, size=self.redraw)
        self.redraw()

    def redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*C('panel')); RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(17)])
            Color(*C('line')); Rectangle(pos=(self.x, self.top-dp(1)), size=(self.width, dp(1)))


class AutoCard(Card):
    """A card that grows with wrapped mobile content."""
    def __init__(self, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('size_hint_y', None)
        super().__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        self.height = dp(24)


class MobileExceptionGuard(ExceptionHandler):
    """Keep recoverable UI callback errors from closing the entire app."""
    def handle_exception(self, exception):
        app = App.get_running_app()
        if app and hasattr(app, 'record_exception'):
            app.record_exception(exception)
            return ExceptionManager.PASS
        return ExceptionManager.RAISE


class PButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault('background_normal', ''); kwargs.setdefault('background_down', '')
        kwargs.setdefault('background_color', C('primary')); kwargs.setdefault('color', (1,1,1,1))
        kwargs.setdefault('size_hint_y', None); kwargs.setdefault('height', dp(48)); kwargs.setdefault('font_size', sp(13))
        super().__init__(**kwargs)
        self.halign = 'center'
        self.valign = 'middle'
        self.bind(size=lambda inst, val: setattr(inst, 'text_size', (max(dp(20), inst.width-dp(12)), inst.height)))


class SButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault('background_normal', ''); kwargs.setdefault('background_down', '')
        kwargs.setdefault('background_color', C('panel2')); kwargs.setdefault('color', C('text'))
        kwargs.setdefault('size_hint_y', None); kwargs.setdefault('height', dp(46)); kwargs.setdefault('font_size', sp(12))
        super().__init__(**kwargs)
        self.halign = 'center'
        self.valign = 'middle'
        self.bind(size=lambda inst, val: setattr(inst, 'text_size', (max(dp(20), inst.width-dp(12)), inst.height)))


class TurkishQKeyboard(Card):
    """Cross-platform in-app Turkish Q keyboard.

    This avoids depending on the user's Android/iOS keyboard language and gives
    the same Turkish-Q layout on both APK and iPhone builds.
    """
    LETTER_ROWS = (
        ('q','w','e','r','t','y','u','ı','o','p','ğ','ü'),
        ('a','s','d','f','g','h','j','k','l','ş','i'),
        ('z','x','c','v','b','n','m','ö','ç'),
    )
    NUMBER_ROWS = (
        ('1','2','3','4','5','6','7','8','9','0'),
        ('@','#','₺','€','$','%','&','*','(',')'),
        ('-','_','+','=','/',':',';','"'),
    )

    def __init__(self, app, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 0)
        kwargs.setdefault('padding', [dp(5), dp(5), dp(5), dp(6)])
        kwargs.setdefault('spacing', dp(4))
        super().__init__(**kwargs)
        self.app = app
        self.target = None
        self.shifted = False
        self.symbols = False
        self.opacity = 0
        self.disabled = True
        self._render()

    def _key(self, text, callback=None, width=None, primary=False):
        cls = PButton if primary else SButton
        btn = cls(text=text, height=dp(39), font_size=sp(10))
        if width is not None:
            btn.size_hint_x = None
            btn.width = dp(width)
        if callback:
            btn.bind(on_release=callback)
        else:
            btn.bind(on_release=lambda inst: self.type_key(inst.text))
        return btn

    def _render(self):
        self.clear_widgets()

        top = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(5))
        title = fit_label(Label(
            text='Türkçe Q', bold=True, font_size=sp(11), color=C('cyan'),
            halign='left', valign='middle'
        ))
        top.add_widget(title)
        close = self._key('Bitti', lambda *_: self.app.hide_turkish_keyboard(), 58, True)
        top.add_widget(close)
        self.add_widget(top)

        rows = self.NUMBER_ROWS if self.symbols else self.LETTER_ROWS
        for letters in rows:
            row = BoxLayout(size_hint_y=None, height=dp(41), spacing=dp(2))
            # Small horizontal breathing room for shorter rows.
            if len(letters) < 12:
                row.padding = [dp(5), 0, dp(5), 0]
            for ch in letters:
                shown = turkish_upper(ch) if self.shifted and not self.symbols else ch
                row.add_widget(self._key(shown))
            self.add_widget(row)

        controls = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(3))
        controls.add_widget(self._key('123' if not self.symbols else 'ABC',
                                      lambda *_: self.toggle_symbols(), 48))
        controls.add_widget(self._key('Shift', lambda *_: self.toggle_shift(), 52))
        controls.add_widget(self._key(',', None, 35))
        controls.add_widget(self._key('.', None, 35))
        controls.add_widget(self._key('?', None, 35))
        space = self._key('Boşluk', lambda *_: self.type_key(' '), None, True)
        controls.add_widget(space)
        controls.add_widget(self._key('Sil', lambda *_: self.backspace(), 46))
        controls.add_widget(self._key('Enter', lambda *_: self.enter_key(), 50))
        self.add_widget(controls)

    def set_target(self, target):
        self.target = target

    def type_key(self, text):
        if not self.target:
            return
        value = normalize_mobile_text(text)
        self.target.insert_text(value)
        # One-shot shift, like a phone keyboard.
        if self.shifted and not self.symbols:
            self.shifted = False
            self._render()

    def backspace(self):
        if not self.target:
            return
        try:
            self.target.do_backspace()
        except Exception:
            idx = self.target.cursor_index()
            if idx > 0:
                self.target.text = self.target.text[:idx-1] + self.target.text[idx:]
                self.target.cursor = self.target.get_cursor_from_index(idx-1)

    def enter_key(self):
        if not self.target:
            return
        if getattr(self.target, 'multiline', False):
            self.target.insert_text('\n')
        else:
            try:
                self.target.dispatch('on_text_validate')
            except Exception:
                pass
            self.app.hide_turkish_keyboard()

    def toggle_shift(self):
        if self.symbols:
            self.symbols = False
        self.shifted = not self.shifted
        self._render()

    def toggle_symbols(self):
        self.symbols = not self.symbols
        self.shifted = False
        self._render()



class Header(BoxLayout):
    def __init__(self, title, app, back='menu', **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(8), **kwargs)
        b = SButton(text='Geri', size_hint_x=None, width=dp(50)); b.bind(on_release=lambda *_: app.go(back)); self.add_widget(b)
        lab = fit_label(Label(text=title, bold=True, font_size=sp(17), color=C('text'), halign='left', valign='middle')); self.add_widget(lab)
        menu = SButton(text='Menü', size_hint_x=None, width=dp(50)); menu.bind(on_release=lambda *_: app.go('menu')); self.add_widget(menu)


class ScrollScreen(Screen):
    def shell(self, title_text, back='menu'):
        app = App.get_running_app()
        root = BoxLayout(orientation='vertical', padding=[dp(14), dp(10), dp(14), dp(8)], spacing=dp(9))
        root.add_widget(Header(title_text, app, back))
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10), padding=[0,0,0,dp(24)])
        content.bind(minimum_height=content.setter('height'))
        scroll.add_widget(content); root.add_widget(scroll); self.add_widget(root)
        return root, content


class SplashScreen(Screen):
    def on_enter(self, *args):
        self.clear_widgets()
        bg = Starfield(); self.add_widget(bg)
        box = BoxLayout(orientation='vertical', size_hint=(.88,.58), pos_hint={'center_x':.5,'center_y':.52}, padding=dp(22), spacing=dp(10))
        bg.add_widget(box)
        card = Card(orientation='vertical', padding=dp(22), spacing=dp(9)); box.add_widget(card)
        card.add_widget(Label(text='12/D', bold=True, font_size=sp(42), color=C('text')))
        card.add_widget(Label(text='DİL PROGRAMI', bold=True, font_size=sp(21), color=C('text')))
        card.add_widget(Label(text='Premium English Hub - Android + iPhone', font_size=sp(11), color=C('cyan')))
        card.add_widget(Label(text=CREDIT, font_size=sp(10), color=C('muted')))
        self.bar = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(14)); card.add_widget(self.bar)
        self.elapsed = 0
        self.ev = Clock.schedule_interval(self._tick, .05)

    def _tick(self, dt):
        self.elapsed += dt; self.bar.value = min(100, self.elapsed/5*100)
        if self.elapsed >= 5:
            self.ev.cancel(); App.get_running_app().after_splash()


class DashboardScreen(ScrollScreen):
    def on_pre_enter(self, *args):
        self.clear_widgets(); _, c = self.shell('Ana Sayfa', 'menu'); app=App.get_running_app(); p=app.db.get_profile()
        if not p: Clock.schedule_once(lambda dt: app.ensure_profile(), 0); return
        c.add_widget(Label(text='12/D • PREMIUM ENGLISH LEARNING', color=C('cyan'), bold=True, font_size=sp(10), size_hint_y=None, height=dp(28)))
        c.add_widget(heading(f"Merhaba, {p['name']}", 25))
        c.add_widget(muted('Bugünkü çalışma rotan hazır. Masaüstündeki öğrenme sistemi telefonda da aynı veritabanı mantığıyla çalışır.', 48))
        row=BoxLayout(size_hint_y=None,height=dp(92),spacing=dp(7))
        for val,note in [(p['current_level'],'SEVİYE'),(p['xp'],'XP'),(f"{p['streak']} gün",'SERİ'),(len(app.db.due_words()),'TEKRAR')]:
            card=Card(orientation='vertical'); card.add_widget(Label(text=str(val),bold=True,font_size=sp(18),color=C('text'))); card.add_widget(Label(text=note,font_size=sp(8),color=C('muted'))); row.add_widget(card)
        c.add_widget(row)
        nxt=app.db.next_lesson(); hero=Card(orientation='vertical',size_hint_y=None,height=dp(180)); hero.add_widget(Label(text='SIRADAKİ ADIM',bold=True,color=C('cyan'),font_size=sp(10)))
        if nxt:
            hero.add_widget(heading(f"{nxt['level_code']} • {nxt['title']}",18,52)); hero.add_widget(muted(nxt['description'],42)); b=PButton(text='Şimdi derse başla →'); b.bind(on_release=lambda *_: app.open_lesson(nxt['id'])); hero.add_widget(b)
        else: hero.add_widget(heading('Erişilebilir tüm dersleri tamamladın',17,70))
        c.add_widget(hero)
        pgr=app.db.current_level_progress(); pc=Card(orientation='vertical',size_hint_y=None,height=dp(115)); pc.add_widget(Label(text=f"{p['current_level']} • {pgr['completed']} / {pgr['total']} ders • %{pgr['percent']}",bold=True,color=C('text'))); pb=ProgressBar(max=100,value=pgr['percent'],size_hint_y=None,height=dp(15)); pc.add_widget(pb); c.add_widget(pc)
        grid=BoxLayout(orientation='vertical',size_hint_y=None,height=dp(226),spacing=dp(7))
        for text,target in [('Kelime Tekrarı','review'),('Listening','listening'),('Speaking','speaking'),('Writing','writing')]:
            b=SButton(text=text); b.bind(on_release=lambda inst,t=target:app.go(t)); grid.add_widget(b)
        c.add_widget(grid)


class MenuScreen(ScrollScreen):
    def on_pre_enter(self,*args):
        self.clear_widgets(); _,c=self.shell('Menü','home'); app=App.get_running_app(); p=app.db.get_profile()
        if p:
            prof=Card(orientation='vertical',size_hint_y=None,height=dp(105)); prof.add_widget(heading(p['name'],18,45)); prof.add_widget(Label(text=f"{p['role']} • {p['current_level']} • {p['xp']} XP",color=C('muted'),font_size=sp(10))); c.add_widget(prof)
        items=[('Dersler','lessons'),('Kelime Merkezi','words'),('Akıllı Tekrar','review'),('Listening Lab','listening'),('Speaking Studio','speaking'),('Reading Room','reading'),('Writing Coach','writing'),('İlerleme','progress'),('Başarımlar','achievements'),('Sınıf Yönetimi','classes'),('Seviye Tespit','placement'),('Profiller','profiles'),('Ayarlar','settings')]
        for txt,target in items:
            b=SButton(text=txt); b.bind(on_release=lambda inst,t=target:app.go(t)); c.add_widget(b)
        cr=Card(orientation='vertical',size_hint_y=None,height=dp(95)); cr.add_widget(Label(text='12/D Dil Programı',bold=True,color=C('text'))); cr.add_widget(Label(text=CREDIT,font_size=sp(9),color=C('muted'))); c.add_widget(cr)


class LessonsScreen(ScrollScreen):
    PAGE_SIZE = 10

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.page = 0
        self.level = None

    def on_pre_enter(self, *args):
        p = App.get_running_app().db.get_profile()
        self.level = self.level or (p['current_level'] if p else 'A1')
        self.render(self.level, self.page)

    def render(self, level=None, page=0):
        self.clear_widgets()
        _, c = self.shell('Dersler', 'menu')
        app = App.get_running_app()
        p = app.db.get_profile()
        level = level or self.level or (p['current_level'] if p else 'A1')
        self.level = level

        sp = Spinner(
            text=level, values=tuple(LEVEL_ORDER), size_hint_y=None, height=dp(48),
            background_normal='', background_color=C('panel2'), color=C('text')
        )
        def _level_changed(inst, value):
            self.page = 0
            self.level = value
            self.render(value, 0)
        sp.bind(text=_level_changed)
        c.add_widget(sp)

        if not app.db.level_accessible(level):
            c.add_widget(self._empty('Bu seviye kilitli. Önce önceki seviyeyi tamamla.'))
            return

        lessons = list(app.db.get_lessons(level))
        total_pages = max(1, (len(lessons) + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        self.page = max(0, min(int(page), total_pages - 1))
        begin = self.page * self.PAGE_SIZE
        rows = lessons[begin:begin + self.PAGE_SIZE]

        c.add_widget(muted(
            f'{level} • {len(lessons)} ders • Sayfa {self.page + 1}/{total_pages}',
            32
        ))

        for lesson in rows:
            accessible = app.db.lesson_accessible(lesson['id'])
            status = 'Tamam' if lesson['completed'] else ('Açık' if accessible else 'Kilitli')
            card = Card(
                orientation='horizontal', size_hint_y=None, height=dp(92),
                spacing=dp(8)
            )
            status_lab = fit_label(Label(
                text=status, size_hint_x=None, width=dp(55),
                color=C('good') if lesson['completed'] else C('cyan') if accessible else C('muted'),
                font_size=sp(9), bold=True, halign='center'
            ))
            card.add_widget(status_lab)

            info = BoxLayout(orientation='vertical')
            info.add_widget(fit_label(Label(
                text=f"{lesson['position']}. {lesson['title']}",
                bold=True, color=C('text'), halign='left', valign='middle'
            )))
            info.add_widget(fit_label(Label(
                text=f"Ünite {lesson['unit']} • En iyi %{lesson['best_score']}",
                font_size=sp(9), color=C('muted'), halign='left', valign='middle'
            )))
            card.add_widget(info)

            b = SButton(text='Aç', size_hint_x=None, width=dp(62))
            b.disabled = not accessible
            if accessible:
                b.bind(on_release=lambda inst, lid=lesson['id']: app.open_lesson(lid))
            card.add_widget(b)
            c.add_widget(card)

        pager = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        prev_b = SButton(text='Önceki')
        next_b = SButton(text='Sonraki')
        prev_b.disabled = self.page <= 0
        next_b.disabled = self.page >= total_pages - 1
        prev_b.bind(on_release=lambda *_: self.render(self.level, self.page - 1))
        next_b.bind(on_release=lambda *_: self.render(self.level, self.page + 1))
        pager.add_widget(prev_b)
        pager.add_widget(next_b)
        c.add_widget(pager)

    def _empty(self, text):
        x = AutoCard()
        x.add_widget(auto_label(text, size=13, bold=True, min_height=52))
        return x


class LessonScreen(ScrollScreen):
    lesson_id = NumericProperty(0)

    def on_pre_enter(self, *args):
        if self.lesson_id:
            Clock.schedule_once(lambda dt: self.render(), 0)

    def render(self):
        app = App.get_running_app()
        try:
            lesson = app.db.get_lesson(self.lesson_id)
            if not lesson:
                app.toast('Ders bulunamadı.')
                app.go('lessons')
                return

            self.clear_widgets()
            _, c = self.shell('Ders', 'lessons')

            c.add_widget(auto_label(
                f"{lesson['level_code']} • Ders {lesson['position']} • {lesson['title']}",
                size=21, bold=True, min_height=58
            ))
            c.add_widget(auto_label(
                lesson['description'], size=11, color_key='muted', min_height=38
            ))

            self._add_text_section(c, 'GRAMMAR', lesson['grammar'])
            self._add_text_section(c, 'ÖRNEK CÜMLE', lesson['example'])
            self._add_text_section(c, 'READING', lesson['reading_text'])

            vocab = safe_json_list(lesson['vocabulary'])
            vcard = AutoCard()
            vcard.add_widget(auto_label('KELİME KARTLARI', size=10, bold=True, color_key='cyan'))
            if vocab:
                for item in vocab:
                    if isinstance(item, dict):
                        word = item.get('word', '')
                        tr = item.get('translation', '')
                        vcard.add_widget(auto_label(f"{word} — {tr}", size=11, min_height=30))
            else:
                vcard.add_widget(auto_label('Kelime verisi bulunamadı.', size=11, color_key='muted'))
            c.add_widget(vcard)

            listen = AutoCard()
            listen.add_widget(auto_label('LISTENING', size=10, bold=True, color_key='cyan'))
            listen.add_widget(auto_label(
                'Metni görmeden dinle. Daha sonra Listening Lab bölümünde kendini değerlendirebilirsin.',
                size=11, color_key='muted', min_height=42
            ))
            play = PButton(text='Listening oynat')
            play.bind(on_release=lambda *_: app.safe_speak(lesson['listening_text']))
            listen.add_widget(play)
            c.add_widget(listen)

            speaking = SButton(text='Speaking Studio')
            speaking.bind(on_release=lambda *_: app.open_skill_for('speaking', self.lesson_id))
            c.add_widget(speaking)

            writing = SButton(text='Writing Coach')
            writing.bind(on_release=lambda *_: app.open_skill_for('writing', self.lesson_id))
            c.add_widget(writing)

            self.quiz = safe_json_list(lesson['quiz'])
            self.quiz_option_groups = []

            qcard = AutoCard()
            qcard.add_widget(auto_label('DERS SONU QUIZ', size=17, bold=True, min_height=42))

            if not self.quiz:
                qcard.add_widget(auto_label(
                    'Bu dersin quiz verisi okunamadı. Uygulamayı yeniden başlatmayı deneyebilirsin.',
                    size=11, color_key='muted', min_height=50
                ))
            else:
                for qidx, q in enumerate(self.quiz):
                    if not isinstance(q, dict):
                        continue
                    question = str(q.get('question', 'Soru'))
                    options = q.get('options') or []
                    if not isinstance(options, list):
                        options = []

                    one = AutoCard(padding=dp(10), spacing=dp(6))
                    one.add_widget(auto_label(
                        f"{qidx + 1}. {question}", size=11, bold=True, min_height=42
                    ))

                    group = f"lesson_{self.lesson_id}_quiz_{qidx}"
                    option_buttons = []
                    for opt_idx, option in enumerate(options):
                        btn = ToggleButton(
                            text=str(option),
                            group=group,
                            allow_no_selection=True,
                            size_hint_y=None,
                            height=dp(46),
                            background_normal='',
                            background_down='',
                            background_color=C('panel2'),
                            color=C('text'),
                            font_size=sp(11),
                        )
                        btn.bind(
                            size=lambda inst, val: setattr(
                                inst, 'text_size',
                                (max(dp(20), inst.width - dp(16)), inst.height)
                            )
                        )
                        option_buttons.append((btn, opt_idx))
                        one.add_widget(btn)

                    self.quiz_option_groups.append((q, option_buttons))
                    qcard.add_widget(one)

                submit = PButton(text='Dersi değerlendir')
                submit.bind(on_release=lambda *_: self.submit_quiz())
                qcard.add_widget(submit)

            c.add_widget(qcard)

        except Exception as exc:
            app.record_exception(exc, context='LessonScreen.render')
            self.clear_widgets()
            _, c = self.shell('Ders açılamadı', 'lessons')
            err = AutoCard()
            err.add_widget(auto_label(
                'Bu ders açılırken bir hata yakalandı. Uygulama artık kapanmayacak. '
                'Ders listesinden başka bir ders deneyebilir veya hata kaydını paylaşabilirsin.',
                size=12, bold=True, min_height=85
            ))
            retry = PButton(text='Dersi tekrar dene')
            retry.bind(on_release=lambda *_: self.render())
            err.add_widget(retry)
            c.add_widget(err)

    def _add_text_section(self, container, title_text, body):
        card = AutoCard()
        card.add_widget(auto_label(title_text, size=10, bold=True, color_key='cyan'))
        card.add_widget(auto_label(body, size=12, min_height=42))
        container.add_widget(card)

    def submit_quiz(self):
        app = App.get_running_app()
        try:
            if not self.quiz_option_groups:
                app.toast('Quiz soruları yüklenemedi.')
                return

            correct = 0
            answered = 0
            for q, buttons in self.quiz_option_groups:
                selected = next((idx for btn, idx in buttons if btn.state == 'down'), None)
                if selected is None:
                    app.toast('Tüm quiz sorularını cevapla.')
                    return
                answered += 1
                try:
                    if selected == int(q.get('correct', -1)):
                        correct += 1
                except (TypeError, ValueError):
                    pass

            score = round(correct / max(1, answered) * 100)
            if score >= 67:
                xp = app.db.complete_lesson(self.lesson_id, score)
                app.toast(f'Ders tamamlandı • %{score} • +{xp} XP')
                Clock.schedule_once(lambda dt: app.go('lessons'), 1.0)
            else:
                app.db.log_activity('Quiz denemesi', 'grammar', score, 3, 3)
                app.toast(f'%{score} • Geçmek için en az %67 gerekiyor.')
        except Exception as exc:
            app.record_exception(exc, context='LessonScreen.submit_quiz')
            app.toast('Quiz sırasında hata yakalandı. Uygulama açık kalacak.')


class WordsScreen(ScrollScreen):
    def on_pre_enter(self,*args): self.render()
    def render(self,query=''):
        self.clear_widgets(); _,c=self.shell('Kelime Merkezi','menu'); app=App.get_running_app(); words=list(app.db.all_words()); due=len(app.db.due_words())
        search=field('İngilizce veya Türkçe ara...',False); c.add_widget(search); search.bind(on_text_validate=lambda inst:self.render(inst.text))
        c.add_widget(muted(f'{len(words)} kelime • {due} tekrar bekliyor • aramak için yazıp Enter’a bas',34))
        q=turkish_lower((query or '').strip()); rows=[w for w in words if not q or q in turkish_lower(w['word']) or q in turkish_lower(w['translation'])]
        if not rows: c.add_widget(self.empty('Henüz eşleşen kelime yok.'))
        for w in rows[:120]:
            card=Card(orientation='horizontal',size_hint_y=None,height=dp(82),spacing=dp(6)); fav=SButton(text='★' if w['favorite'] else '☆',size_hint_x=None,width=dp(46)); fav.bind(on_release=lambda inst,wid=w['id']:self.toggle(wid)); card.add_widget(fav)
            info=BoxLayout(orientation='vertical'); info.add_widget(fit_label(Label(text=f"{w['word']} — {w['translation']}",bold=True,color=C('text'),halign='left'))); info.add_widget(fit_label(Label(text=f"{w['level_code']} • tekrar: {w['due_date']}",font_size=sp(9),color=C('muted'),halign='left'))); card.add_widget(info)
            t=SButton(text='🔊',size_hint_x=None,width=dp(48)); t.bind(on_release=lambda inst,word=w['word']:app.safe_speak(word)); card.add_widget(t); c.add_widget(card)
    def toggle(self,wid): App.get_running_app().db.toggle_favorite(wid); self.render()
    def empty(self,text): x=Card(orientation='vertical',size_hint_y=None,height=dp(100)); x.add_widget(Label(text=text,color=C('text'))); return x


class ReviewScreen(ScrollScreen):
    def on_pre_enter(self,*args): self.words=list(App.get_running_app().db.due_words()); self.index=0; self.revealed=False; self.render()
    def render(self):
        self.clear_widgets(); _,c=self.shell('Akıllı Tekrar','menu'); app=App.get_running_app()
        if self.index>=len(self.words): c.add_widget(heading('Bugün bekleyen tekrar kalmadı',19,75)); return
        w=self.words[self.index]; c.add_widget(muted(f'{self.index+1}/{len(self.words)} • Önce anlamı hatırlamaya çalış',34)); card=Card(orientation='vertical',size_hint_y=None,height=dp(250)); card.add_widget(heading(w['word'],30,70)); self.answer=Label(text='Cevap gizli',color=C('muted'),font_size=sp(14)); card.add_widget(self.answer); reveal=PButton(text='Anlamı göster'); reveal.bind(on_release=lambda *_:self.reveal(w)); card.add_widget(reveal); self.ratebox=BoxLayout(size_hint_y=None,height=dp(48),spacing=dp(5)); card.add_widget(self.ratebox); c.add_widget(card)
    def reveal(self,w):
        self.revealed=True; self.answer.text=f"{w['translation']}\nÖrnek: {w['example'] or '—'}"; self.ratebox.clear_widgets()
        for label,q in [('Zor','hard'),('Orta','medium'),('Kolay','easy')]:
            b=SButton(text=label); b.bind(on_release=lambda inst,quality=q:self.rate(quality)); self.ratebox.add_widget(b)
    def rate(self,q):
        if not self.revealed:return
        App.get_running_app().db.review_word(self.words[self.index]['id'],q); self.index+=1; self.revealed=False; self.render()


class SkillBase(ScrollScreen):
    mode=''; screen_title=''
    def on_pre_enter(self,*args): self.render(getattr(self,'requested_lesson_id',0) or 0)
    def accessible(self):
        app=App.get_running_app(); rows=[]
        for level in LEVEL_ORDER:
            if app.db.level_accessible(level): rows.extend(app.db.get_lessons(level))
        return rows
    def render(self,lid=0):
        self.clear_widgets(); _,c=self.shell(self.screen_title,'menu'); app=App.get_running_app(); rows=self.accessible()
        if not rows: c.add_widget(heading('Erişilebilir ders yok.',18)); return
        l=next((x for x in rows if x['id']==lid),rows[0]); self.selected_id=l['id']
        values=tuple(f"{x['level_code']} • {x['position']} • {x['title']}" for x in rows); mp={v:x['id'] for v,x in zip(values,rows)}; current=next(k for k,v in mp.items() if v==l['id'])
        sp=Spinner(text=current,values=values,size_hint_y=None,height=dp(48),background_normal='',background_color=C('panel2'),color=C('text')); sp.bind(text=lambda inst,v:self.render(mp[v])); c.add_widget(sp); self.build_body(c,l)
    def build_body(self,c,l): pass


class ListeningScreen(SkillBase):
    mode='listening'; screen_title='Listening Lab'
    def build_body(self,c,l):
        app=App.get_running_app(); card=Card(orientation='vertical',size_hint_y=None,height=dp(290)); card.add_widget(muted('Metni görmeden dinle. Sonra duyduğunu/hatırladığını İngilizce yaz.',52)); b=PButton(text='Listening’i oynat'); b.bind(on_release=lambda *_:app.safe_speak(l['listening_text'])); card.add_widget(b); self.input=field('Duyduğun cümleyi yaz...',True,105); card.add_widget(self.input); ev=SButton(text='Listening puanını hesapla'); ev.bind(on_release=lambda *_:self.eval(l)); card.add_widget(ev); c.add_widget(card)
    def eval(self,l): score=speaking_score(l['listening_text'],self.input.text); App.get_running_app().db.log_activity('Listening pratiği','listening',score,8,5); App.get_running_app().toast(f'Listening puanı: %{score}')


class SpeakingScreen(SkillBase):
    mode='speaking'; screen_title='Speaking Studio'
    def build_body(self,c,l):
        app=App.get_running_app(); card=Card(orientation='vertical',size_hint_y=None,height=dp(355)); card.add_widget(muted('Hedef cümleyi dinle, sonra İngilizce söyle. Android’de uygulama mikrofonunu; iPhone’da klavye diktesini kullanabilirsin.',60)); self.target=fit_label(Label(text=l['speaking_prompt'],bold=True,font_size=sp(16),color=C('text'),halign='left',size_hint_y=None,height=dp(70))); card.add_widget(self.target); hear=SButton(text='Hedefi dinle'); hear.bind(on_release=lambda *_:app.safe_speak(l['speaking_prompt'])); card.add_widget(hear); self.input=field('Konuşman / algılanan metin...',True,90); card.add_widget(self.input); mic=SButton(text='Mikrofonla konuş'); mic.bind(on_release=lambda *_:app.speech.recognize_english(self.on_recognition)); card.add_widget(mic); ev=PButton(text='Benzerlik puanını hesapla'); ev.bind(on_release=lambda *_:self.eval(l)); card.add_widget(ev); c.add_widget(card)
    def on_recognition(self,ok,text):
        if ok:self.input.text=text; App.get_running_app().toast('Konuşma algılandı.')
        else:App.get_running_app().toast(text)
    def eval(self,l): score=speaking_score(l['speaking_prompt'],self.input.text); App.get_running_app().db.log_activity('Speaking pratiği','speaking',score,10,5); App.get_running_app().toast(f'Speaking puanı: %{score}')


class ReadingScreen(SkillBase):
    screen_title='Reading Room'
    def build_body(self,c,l):
        app=App.get_running_app(); card=Card(orientation='vertical',size_hint_y=None,height=dp(350)); card.add_widget(fit_label(Label(text=l['reading_text'],color=C('text'),font_size=sp(12),halign='left',valign='top',size_hint_y=None,height=dp(150)))); self.input=field('Metnin ana fikrini İngilizce bir cümleyle yaz...',True,90); card.add_widget(self.input); b=PButton(text='Reading puanını hesapla'); b.bind(on_release=lambda *_:self.eval(l)); card.add_widget(b); c.add_widget(card)
    def eval(self,l):
        score=speaking_score(l['reading_text'],self.input.text); score=max(35,score) if self.input.text.strip() else 0; App.get_running_app().db.log_activity('Reading pratiği','reading',score,8,5); App.get_running_app().toast(f'Reading puanı: %{score}')


class WritingScreen(SkillBase):
    screen_title='Writing Coach'
    def build_body(self,c,l):
        card=Card(orientation='vertical',size_hint_y=None,height=dp(450)); card.add_widget(fit_label(Label(text=l['writing_prompt'],bold=True,color=C('text'),font_size=sp(13),halign='left',size_hint_y=None,height=dp(85)))); self.input=field('İngilizce metnini yaz...',True,230); card.add_widget(self.input); b=PButton(text='Yazımı değerlendir'); b.bind(on_release=lambda *_:self.eval(l)); card.add_widget(b); c.add_widget(card)
    def eval(self,l):
        score,notes=writing_score(self.input.text,l['level_code']); App.get_running_app().db.log_activity('Writing pratiği','writing',score,12,8); App.get_running_app().result_popup(f'Writing • %{score}','\n'.join(notes))


class ProgressScreen(ScrollScreen):
    def on_pre_enter(self,*args):
        self.clear_widgets(); _,c=self.shell('İlerleme ve İstatistik','menu'); app=App.get_running_app(); s=app.db.stats(); p=app.db.get_profile(); level=app.db.current_level_progress()
        row=BoxLayout(size_hint_y=None,height=dp(92),spacing=dp(6))
        for t,v in [('Ders',f"{s['completed']}/{s['total']}"),('Çalışma',f"{s['minutes']} dk"),('Kelime',s['words']),('XP',s['xp'])]:
            x=Card(orientation='vertical'); x.add_widget(Label(text=str(v),bold=True,font_size=sp(16),color=C('text'))); x.add_widget(Label(text=t,font_size=sp(8),color=C('muted'))); row.add_widget(x)
        c.add_widget(row)
        x=Card(orientation='vertical',size_hint_y=None,height=dp(110)); x.add_widget(Label(text=f"{p['current_level']} • {level['completed']}/{level['total']} ders • %{level['percent']}",bold=True,color=C('text'))); pb=ProgressBar(max=100,value=level['percent'],size_hint_y=None,height=dp(15)); x.add_widget(pb); c.add_widget(x)
        scores=app.db.skill_scores(); names={'vocabulary':'Kelime','grammar':'Grammar','reading':'Reading','listening':'Listening','speaking':'Speaking','writing':'Writing'}
        sc=Card(orientation='vertical',size_hint_y=None,height=dp(80+len(scores)*52)); sc.add_widget(heading('Beceri Puanları',17,42))
        for k,v in scores.items():
            r=BoxLayout(size_hint_y=None,height=dp(42),spacing=dp(6)); r.add_widget(Label(text=names[k],size_hint_x=None,width=dp(70),color=C('text'),font_size=sp(10))); pb=ProgressBar(max=100,value=v); r.add_widget(pb); r.add_widget(Label(text=f'%{v}',size_hint_x=None,width=dp(44),color=C('muted'),font_size=sp(9))); sc.add_widget(r)
        c.add_widget(sc)
        week=app.db.weekly_minutes(); wc=Card(orientation='vertical',size_hint_y=None,height=dp(70+len(week)*45)); wc.add_widget(heading('Son 7 Gün',17,42)); peak=max([x['minutes'] for x in week] or [1])
        for x in week:
            r=BoxLayout(size_hint_y=None,height=dp(38)); r.add_widget(Label(text=x['label'],size_hint_x=None,width=dp(55),color=C('text'),font_size=sp(10))); pb=ProgressBar(max=max(1,peak),value=x['minutes']); r.add_widget(pb); r.add_widget(Label(text=f"{x['minutes']} dk",size_hint_x=None,width=dp(55),color=C('muted'),font_size=sp(9))); wc.add_widget(r)
        c.add_widget(wc)


class AchievementsScreen(ScrollScreen):
    def on_pre_enter(self,*args):
        self.clear_widgets(); _,c=self.shell('Başarımlar','menu'); app=App.get_running_app()
        for a in app.db.achievements():
            x=Card(orientation='horizontal',size_hint_y=None,height=dp(78)); x.add_widget(Label(text='AÇIK' if a['unlocked'] else 'KİLİT',size_hint_x=None,width=dp(52),font_size=sp(8),bold=True,color=C('good') if a['unlocked'] else C('muted'))); info=BoxLayout(orientation='vertical'); info.add_widget(fit_label(Label(text=a['title'],bold=True,color=C('text'),halign='left'))); info.add_widget(fit_label(Label(text='Açıldı' if a['unlocked'] else 'Henüz kilitli',font_size=sp(9),color=C('good') if a['unlocked'] else C('muted'),halign='left'))); x.add_widget(info); c.add_widget(x)


class PlacementScreen(ScrollScreen):
    def on_pre_enter(self,*args):
        self.clear_widgets(); _,c=self.shell('Seviye Tespit Sınavı','menu'); self.answers=[]; c.add_widget(muted('A1’den C2’ye tahmini seviyeni yeniden ölç. Mevcut ders ilerlemen silinmez.',48))
        for i,(level,q,opts,correct) in enumerate(PLACEMENT_QUESTIONS):
            card=Card(orientation='vertical',size_hint_y=None,height=dp(128)); card.add_widget(Label(text=f'{i+1}/{len(PLACEMENT_QUESTIONS)} • {level}',color=C('cyan'),font_size=sp(9))); card.add_widget(fit_label(Label(text=q,bold=True,color=C('text'),font_size=sp(11),halign='left',size_hint_y=None,height=dp(40)))); sp=Spinner(text='Cevap seç',values=tuple(opts),size_hint_y=None,height=dp(42),background_normal='',background_color=C('panel2'),color=C('text')); self.answers.append((sp,opts,correct)); card.add_widget(sp); c.add_widget(card)
        b=PButton(text='Testi bitir ve seviyemi hesapla'); b.bind(on_release=lambda *_:self.finish()); c.add_widget(b)
    def finish(self):
        app=App.get_running_app(); correct=0
        for sp,opts,ci in self.answers:
            if sp.text=='Cevap seç': app.toast('Tüm soruları cevapla.'); return
            if opts.index(sp.text)==ci: correct+=1
        score=round(correct/len(self.answers)*100)
        level='A1' if score<28 else 'A2' if score<45 else 'B1' if score<62 else 'B2' if score<76 else 'C1' if score<90 else 'C2'
        app.db.save_placement(score,level); app.result_popup('Seviye Tespit Sonucu',f'Puan: %{score}\nTahmini seviye: {level}\n\nAlt seviyelerdeki dersleri tekrar edebilirsin.')


class SettingsScreen(ScrollScreen):
    def on_pre_enter(self,*args):
        self.clear_widgets(); _,c=self.shell('Ayarlar','menu'); app=App.get_running_app(); p=app.db.get_profile(); card=Card(orientation='vertical',size_hint_y=None,height=dp(420)); card.add_widget(Label(text='PROFİL VE UYGULAMA',bold=True,color=C('cyan'),font_size=sp(9))); self.name=field('Ad'); self.name.text=p['name']; card.add_widget(self.name); self.goal=field('Günlük hedef'); self.goal.text=str(p['daily_goal']); card.add_widget(self.goal); self.theme=Spinner(text='Koyu tema' if p['theme']=='dark' else 'Açık tema',values=('Koyu tema','Açık tema'),size_hint_y=None,height=dp(48),background_normal='',background_color=C('panel2'),color=C('text')); card.add_widget(self.theme); self.rate=field('Ses hızı'); self.rate.text=str(p['tts_rate']); card.add_widget(self.rate); save=PButton(text='Ayarları kaydet'); save.bind(on_release=lambda *_:self.save()); card.add_widget(save); test=SButton(text='Sesi test et'); test.bind(on_release=lambda *_:app.safe_speak('Hello! Welcome to the 12 D Language Program.')); card.add_widget(test); c.add_widget(card)
    def save(self):
        app=App.get_running_app()
        try: goal=max(5,min(180,int(self.goal.text))); rate=max(100,min(260,int(self.rate.text)))
        except: app.toast('Günlük hedef veya ses hızı geçersiz.'); return
        theme='dark' if self.theme.text.startswith('Koyu') else 'light'; app.db.update_profile(self.name.text.strip(),goal,theme,rate); app.theme_name=theme; Window.clearcolor=C('bg'); app.toast('Ayarlar kaydedildi. Tema uygulandı.'); self.on_pre_enter()


class ProfilesScreen(ScrollScreen):
    def on_pre_enter(self,*args): self.render()
    def render(self):
        self.clear_widgets(); _,c=self.shell('Profil Yönetimi','menu'); app=App.get_running_app(); b=PButton(text='+ Yeni Profil'); b.bind(on_release=lambda *_:app.profile_popup(False)); c.add_widget(b)
        for p in app.db.list_profiles():
            card=Card(orientation='horizontal',size_hint_y=None,height=dp(86),spacing=dp(6)); info=BoxLayout(orientation='vertical'); info.add_widget(fit_label(Label(text=('AKTİF ' if p['active'] else '')+p['name'],bold=True,color=C('text'),halign='left'))); info.add_widget(fit_label(Label(text=f"{p['role']} • {p['current_level']} • {p['xp']} XP",font_size=sp(9),color=C('muted'),halign='left'))); card.add_widget(info); choose=SButton(text='Seç',size_hint_x=None,width=dp(58)); choose.bind(on_release=lambda inst,pid=p['id']:self.switch(pid)); card.add_widget(choose); delete=SButton(text='Sil',size_hint_x=None,width=dp(56),background_color=C('danger')); delete.bind(on_release=lambda inst,pid=p['id'],name=p['name']:app.delete_profile_confirm(pid,name)); card.add_widget(delete); c.add_widget(card)
    def switch(self,pid): App.get_running_app().db.switch_profile(pid); App.get_running_app().sync_theme_from_profile(); App.get_running_app().toast('Profil değiştirildi.'); App.get_running_app().go('home')


class ClassesScreen(ScrollScreen):
    def on_pre_enter(self,*args): self.render()
    def render(self):
        self.clear_widgets(); _,c=self.shell('Sınıf Yönetimi','menu'); app=App.get_running_app(); add=PButton(text='+ Yeni Sınıf Oluştur'); add.bind(on_release=lambda *_:app.create_class_popup(self)); c.add_widget(add)
        classes=app.db.list_classes()
        if not classes: c.add_widget(muted('Henüz sınıf yok. Yeni Sınıf ile oluşturabilirsin.',45))
        for cls in classes:
            plans=app.db.list_class_plans(cls['id']); done=sum(1 for x in plans if x['status']=='İşlendi'); card=Card(orientation='vertical',size_hint_y=None,height=dp(145)); card.add_widget(heading(f"{cls['name']} • {cls['level_code']}",17,42)); card.add_widget(muted(f"{cls['academic_year'] or 'Yıl belirtilmedi'} • {done}/{len(plans)} plan işlendi",32)); row=BoxLayout(size_hint_y=None,height=dp(46),spacing=dp(6)); openb=SButton(text='Yönet'); openb.bind(on_release=lambda inst,cid=cls['id']:app.open_class(cid)); row.add_widget(openb); delb=SButton(text='Sınıfı Sil',background_color=C('danger')); delb.bind(on_release=lambda inst,cid=cls['id'],name=cls['name']:app.delete_class_confirm(cid,name)); row.add_widget(delb); card.add_widget(row); c.add_widget(card)


class ClassDetailScreen(ScrollScreen):
    class_id=NumericProperty(0)
    def show_class(self,cid): self.class_id=cid; Clock.schedule_once(lambda dt:self.render(),0)
    def render(self):
        self.clear_widgets(); _,c=self.shell('Sınıf ve Ders Planı','classes'); app=App.get_running_app(); cls=app.db.get_class(self.class_id)
        if not cls:app.go('classes');return
        c.add_widget(heading(f"{cls['name']} • {cls['level_code']}",23,62)); c.add_widget(muted(f"{cls['academic_year'] or 'Eğitim yılı belirtilmedi'}\n{cls['notes'] or 'Sınıf notu yok.'}",48)); add=PButton(text='+ Ders Planına Ekle'); add.bind(on_release=lambda *_:app.class_plan_popup(self.class_id,self)); c.add_widget(add)
        plans=app.db.list_class_plans(self.class_id)
        if not plans:c.add_widget(muted('Henüz ders planı yok.',38))
        for p in plans:
            card=Card(orientation='vertical',size_hint_y=None,height=dp(145)); card.add_widget(fit_label(Label(text=f"{p['planned_date'] or 'Tarih yok'} • {p['level_code']} • Ders {p['position']}\n{p['lesson_title']}",bold=True,color=C('text'),halign='left'))); card.add_widget(muted(f"{p['status']} • {p['notes'] or 'Not yok'}",30)); row=BoxLayout(size_hint_y=None,height=dp(42),spacing=dp(6)); status=SButton(text='Bekliyor yap' if p['status']=='İşlendi' else 'İşlendi yap'); status.bind(on_release=lambda inst,pid=p['id'],st=p['status']:self.status(pid,st)); row.add_widget(status); dele=SButton(text='Planı Sil',background_color=C('danger')); dele.bind(on_release=lambda inst,pid=p['id']:self.delete_plan(pid)); row.add_widget(dele); card.add_widget(row); c.add_widget(card)
    def status(self,pid,current): App.get_running_app().db.set_class_plan_status(pid,'Bekliyor' if current=='İşlendi' else 'İşlendi'); self.render()
    def delete_plan(self,pid): App.get_running_app().db.delete_class_plan(pid); self.render()


class Universal12DApp(App):
    def build(self):
        self.title = APP_NAME
        self.theme_name = 'dark'
        configure_mobile_text_environment()
        Window.clearcolor = C('bg')
        # Keep the software keyboard below/near the active field instead of covering it.
        try:
            Window.softinput_mode = 'below_target'
        except Exception:
            pass

        db_path = Path(self.user_data_dir) / '12d_dil_programi.db'
        self.error_log_path = Path(self.user_data_dir) / 'mobile_error.log'
        self.db = Database(db_path)
        self.db.initialize()
        self.sync_theme_from_profile()
        self.speech = MobileSpeech(self)

        self.sm = ScreenManager(transition=SlideTransition(duration=.12))
        screens = [
            SplashScreen(name='splash'), DashboardScreen(name='home'),
            MenuScreen(name='menu'), LessonsScreen(name='lessons'),
            LessonScreen(name='lesson'), WordsScreen(name='words'),
            ReviewScreen(name='review'), ListeningScreen(name='listening'),
            SpeakingScreen(name='speaking'), ReadingScreen(name='reading'),
            WritingScreen(name='writing'), ProgressScreen(name='progress'),
            AchievementsScreen(name='achievements'),
            PlacementScreen(name='placement'), SettingsScreen(name='settings'),
            ProfilesScreen(name='profiles'), ClassesScreen(name='classes'),
            ClassDetailScreen(name='class_detail')
        ]
        for screen in screens:
            self.sm.add_widget(screen)

        # Recoverable button/screen callback errors are logged instead of killing
        # the Android/iOS process.
        ExceptionManager.add_handler(MobileExceptionGuard())

        self.turkish_keyboard = TurkishQKeyboard(self)
        self.mobile_root = BoxLayout(orientation='vertical')
        self.mobile_root.add_widget(self.sm)
        self.mobile_root.add_widget(self.turkish_keyboard)

        self.sm.current = 'splash'
        return self.mobile_root
    def show_turkish_keyboard(self, target):
        """Show the same Turkish-Q keyboard on Android and iPhone."""
        try:
            if not hasattr(self, 'turkish_keyboard'):
                return
            self.turkish_keyboard.set_target(target)
            self.turkish_keyboard.disabled = False
            self.turkish_keyboard.opacity = 1
            self.turkish_keyboard.height = dp(215)
        except Exception as exc:
            self.record_exception(exc, context='show_turkish_keyboard')

    def hide_turkish_keyboard(self):
        try:
            if not hasattr(self, 'turkish_keyboard'):
                return
            target = self.turkish_keyboard.target
            self.turkish_keyboard.height = 0
            self.turkish_keyboard.opacity = 0
            self.turkish_keyboard.disabled = True
            self.turkish_keyboard.set_target(None)
            if target:
                target.focus = False
        except Exception as exc:
            self.record_exception(exc, context='hide_turkish_keyboard')

    def sync_theme_from_profile(self):
        p=self.db.get_profile() if hasattr(self,'db') else None; self.theme_name=(p['theme'] if p and p['theme'] in THEMES else 'dark'); Window.clearcolor=C('bg')
    def after_splash(self):
        self.ensure_profile() if not self.db.has_profiles() else self.go('home')

    def ensure_profile(self):
        self.profile_popup(True)

    def go(self, name):
        try:
            self.hide_turkish_keyboard()
            if name != 'splash' and not self.db.has_profiles():
                self.ensure_profile()
                return
            if not self.sm.has_screen(name):
                self.toast('Ekran bulunamadı.')
                return
            self.sm.current = name
        except Exception as exc:
            self.record_exception(exc, context=f'go:{name}')
            if self.sm.has_screen('home'):
                self.sm.current = 'home'

    def open_lesson(self, lid):
        try:
            self.hide_turkish_keyboard()
            lesson = self.db.get_lesson(lid)
            if not lesson:
                self.toast('Ders bulunamadı.')
                return
            if not self.db.lesson_accessible(lid):
                self.toast('Bu ders henüz kilitli.')
                return
            screen = self.sm.get_screen('lesson')
            screen.lesson_id = int(lid)
            self.sm.current = 'lesson'
        except Exception as exc:
            self.record_exception(exc, context=f'open_lesson:{lid}')
            self.toast('Ders açılırken hata yakalandı. Uygulama açık kalacak.')

    def open_class(self, cid):
        try:
            self.hide_turkish_keyboard()
            screen = self.sm.get_screen('class_detail')
            screen.class_id = int(cid)
            self.sm.current = 'class_detail'
            Clock.schedule_once(lambda dt: screen.render(), 0)
        except Exception as exc:
            self.record_exception(exc, context=f'open_class:{cid}')
            self.toast('Sınıf açılırken hata yakalandı.')

    def open_skill_for(self, screen, lid):
        try:
            self.hide_turkish_keyboard()
            target = self.sm.get_screen(screen)
            target.requested_lesson_id = int(lid)
            self.sm.current = screen
        except Exception as exc:
            self.record_exception(exc, context=f'open_skill:{screen}:{lid}')
            self.toast('Beceri ekranı açılamadı.')

    def safe_speak(self, text):
        try:
            profile = self.db.get_profile()
            rate = profile['tts_rate'] if profile else 165
            self.speech.speak(text, rate)
        except Exception as exc:
            self.record_exception(exc, context='safe_speak')
            self.toast('Seslendirme başlatılamadı.')

    def record_exception(self, exception, context='mobile-ui'):
        try:
            stamp = __import__('datetime').datetime.now().isoformat(timespec='seconds')
            details = ''.join(traceback.format_exception(
                type(exception), exception, exception.__traceback__
            ))
            with self.error_log_path.open('a', encoding='utf-8') as fh:
                fh.write(f"\n[{stamp}] {context}\n{details}\n")
        except Exception:
            pass

        def _notify(dt):
            try:
                self.toast('Bir mobil arayüz hatası yakalandı; uygulama kapatılmadı.')
            except Exception:
                pass
        Clock.schedule_once(_notify, 0)
    def toast(self,message):
        view=ModalView(size_hint=(.9,None),height=dp(68),background_color=(0,0,0,0)); card=Card(); card.add_widget(fit_label(Label(text=message,color=C('text'),bold=True,halign='center'))); view.add_widget(card); view.open(); Clock.schedule_once(lambda dt:view.dismiss(),1.7)
    def result_popup(self,title_text,body):
        content=BoxLayout(orientation='vertical',padding=dp(16),spacing=dp(10)); content.add_widget(heading(title_text,19,50)); content.add_widget(muted(body,150)); ok=PButton(text='Tamam'); content.add_widget(ok); pop=Popup(title='',content=content,size_hint=(.92,None),height=dp(300),background=''); ok.bind(on_release=lambda *_:pop.dismiss()); pop.open()
    def profile_popup(self,mandatory=False):
        content=BoxLayout(orientation='vertical',padding=dp(16),spacing=dp(9)); content.add_widget(heading('İlk profilini oluştur' if mandatory else 'Yeni Profil',20,50));
        if mandatory:content.add_widget(muted('Profil oluşturmadan uygulamaya erişilemez. Bu ekran yalnızca profil yokken zorunludur.',52))
        name=field('Profil adı'); role=Spinner(text='Öğretmen',values=('Öğretmen','Öğrenci'),size_hint_y=None,height=dp(46)); level=Spinner(text='A1',values=tuple(LEVEL_ORDER),size_hint_y=None,height=dp(46)); goal=field('Günlük hedef (dakika)'); goal.text='20'; content.add_widget(name);content.add_widget(role);content.add_widget(level);content.add_widget(goal); save=PButton(text='Profili Oluştur ve Devam Et'); content.add_widget(save)
        pop=Popup(title='',content=content,size_hint=(.94,None),height=dp(455),auto_dismiss=not mandatory,background='')
        def create(*_):
            try: g=max(5,min(180,int(goal.text or '20'))); pid=self.db.create_profile(name.text,role.text,level.text,g); self.db.switch_profile(pid)
            except Exception as exc:self.toast(str(exc));return
            self.sync_theme_from_profile(); pop.dismiss(); self.go('home')
        save.bind(on_release=create); pop.open()
    def delete_profile_confirm(self,pid,name):
        content=BoxLayout(orientation='vertical',padding=dp(15),spacing=dp(10)); content.add_widget(heading('Profili Sil',19,48)); content.add_widget(muted(f'Bu profili silmek istediğinize emin misiniz?\n\nProfil: {name}\nİlerleme, XP, kelimeler ve profile bağlı sınıf verileri de silinir.',120)); row=BoxLayout(size_hint_y=None,height=dp(48),spacing=dp(7)); no=SButton(text='Hayır'); yes=PButton(text='Evet, Profili Sil',background_color=C('danger')); row.add_widget(no);row.add_widget(yes);content.add_widget(row); pop=Popup(title='',content=content,size_hint=(.94,None),height=dp(320),background=''); no.bind(on_release=lambda *_:pop.dismiss())
        def delete(*_):
            remain=self.db.delete_profile(pid);pop.dismiss()
            if not remain:self.ensure_profile()
            else:self.sync_theme_from_profile();self.go('profiles')
        yes.bind(on_release=delete);pop.open()
    def create_class_popup(self,screen):
        content=BoxLayout(orientation='vertical',padding=dp(14),spacing=dp(8)); name=field('Sınıf adı (örn. 12/D)'); level=Spinner(text='A1',values=tuple(LEVEL_ORDER),size_hint_y=None,height=dp(46)); year=field('Eğitim yılı (örn. 2026-2027)'); notes=field('Sınıf notu',True,80); content.add_widget(name);content.add_widget(level);content.add_widget(year);content.add_widget(notes);save=PButton(text='Sınıfı Oluştur');content.add_widget(save);pop=Popup(title='Yeni Sınıf',content=content,size_hint=(.94,None),height=dp(410))
        def create(*_):
            try:self.db.create_class(name.text,level.text,year.text,notes.text)
            except Exception as exc:self.toast(str(exc));return
            pop.dismiss();screen.render()
        save.bind(on_release=create);pop.open()
    def delete_class_confirm(self,cid,name):
        content=BoxLayout(orientation='vertical',padding=dp(14),spacing=dp(10));content.add_widget(heading('Sınıfı Sil',18,48));content.add_widget(muted(f"'{name}' sınıfını ve tüm ders planlarını silmek istediğinize emin misiniz?",85));row=BoxLayout(size_hint_y=None,height=dp(48),spacing=dp(7));no=SButton(text='Hayır');yes=PButton(text='Evet, Sil',background_color=C('danger'));row.add_widget(no);row.add_widget(yes);content.add_widget(row);pop=Popup(title='',content=content,size_hint=(.92,None),height=dp(260),background='');no.bind(on_release=lambda *_:pop.dismiss());yes.bind(on_release=lambda *_:(self.db.delete_class(cid),pop.dismiss(),self.sm.get_screen('classes').render()));pop.open()
    def class_plan_popup(self,cid,screen):
        cls=self.db.get_class(cid);lessons=self.db.get_lessons(cls['level_code']);values=tuple(f"{l['position']}. {l['title']}" for l in lessons);mapping={f"{l['position']}. {l['title']}":l['id'] for l in lessons};content=BoxLayout(orientation='vertical',padding=dp(14),spacing=dp(8));lesson=Spinner(text=values[0] if values else 'Ders yok',values=values,size_hint_y=None,height=dp(46));dt=field('Tarih YYYY-MM-DD');dt.text=date.today().isoformat();notes=field('Öğretmen notu',True,85);content.add_widget(lesson);content.add_widget(dt);content.add_widget(notes);save=PButton(text='Ders Planına Ekle');content.add_widget(save);pop=Popup(title=f"{cls['name']} • Ders Planı",content=content,size_hint=(.94,None),height=dp(385))
        def add(*_):
            if not values:return
            self.db.add_class_plan(cid,mapping[lesson.text],dt.text,notes.text);pop.dismiss();screen.render()
        save.bind(on_release=add);pop.open()

if __name__=='__main__':
    Universal12DApp().run()
