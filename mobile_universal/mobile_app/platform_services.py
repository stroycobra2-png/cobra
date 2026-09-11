"""Android + iOS platform services.

TTS is native on both supported mobile platforms. Android speech recognition uses
RecognizerIntent. On iOS, the Speaking screen always supports keyboard dictation
and manual input; a direct recognition button falls back to a clear instruction
because iOS Speech framework integration requires Apple signing/entitlements.
"""
from kivy.clock import Clock
from kivy.utils import platform


def configure_mobile_text_environment():
    """Set safe app-locale hints; the OS keyboard layout remains user-owned."""
    if platform == 'android':
        try:
            from jnius import autoclass
            Locale = autoclass('java.util.Locale')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            locale = Locale('tr', 'TR')
            Locale.setDefault(locale)
            activity = PythonActivity.mActivity
            resources = activity.getResources()
            config = resources.getConfiguration()
            try:
                config.setLocale(locale)
            except Exception:
                config.locale = locale
            resources.updateConfiguration(config, resources.getDisplayMetrics())
        except Exception:
            pass


class MobileSpeech:
    def __init__(self, app):
        self.app = app
        self._android_tts = None
        self._activity_result_bound = False
        self._speech_request_code = 12012
        self._speech_callback = None

    def speak(self, text, rate=165):
        text = (text or '').strip()
        if not text:
            return
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
                Locale = autoclass('java.util.Locale')
                activity = PythonActivity.mActivity
                if self._android_tts is None:
                    self._android_tts = TextToSpeech(activity, None)
                self._android_tts.setLanguage(Locale.US)
                self._android_tts.setSpeechRate(max(0.55, min(1.6, float(rate) / 165.0)))
                self._android_tts.speak(text, TextToSpeech.QUEUE_FLUSH, None, '12d_tts')
                return
            except Exception as exc:
                self.app.toast(f'Seslendirme kullanılamadı: {exc}')
                return
        if platform == 'ios':
            try:
                from pyobjus import autoclass
                AVSpeechSynthesizer = autoclass('AVSpeechSynthesizer')
                AVSpeechUtterance = autoclass('AVSpeechUtterance')
                synth = AVSpeechSynthesizer.alloc().init()
                utterance = AVSpeechUtterance.speechUtteranceWithString_(text)
                utterance.rate = max(0.35, min(0.58, 0.46 * float(rate) / 165.0))
                synth.speakUtterance_(utterance)
                self._ios_synth = synth
                return
            except Exception as exc:
                self.app.toast(f'iPhone seslendirme kullanılamadı: {exc}')
                return
        # Desktop development fallback.
        self.app.toast('TTS telefon paketinde Android/iPhone üzerinde çalışır.')

    def recognize_english(self, callback):
        if platform == 'android':
            try:
                from android import activity
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                RecognizerIntent = autoclass('android.speech.RecognizerIntent')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                self._speech_callback = callback
                if not self._activity_result_bound:
                    activity.bind(on_activity_result=self._on_activity_result)
                    self._activity_result_bound = True
                intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, 'en-US')
                intent.putExtra(RecognizerIntent.EXTRA_PROMPT, 'Speak English')
                PythonActivity.mActivity.startActivityForResult(intent, self._speech_request_code)
                return
            except Exception as exc:
                callback(False, f'Mikrofon açılamadı: {exc}')
                return
        if platform == 'ios':
            callback(False, 'iPhone’da bu ekrandaki metin alanına dokunup iOS klavyesindeki mikrofon/dikte düğmesini kullanabilirsin.')
            return
        callback(False, 'Konuşma algılama Android/iPhone paketinde kullanılabilir.')

    def _on_activity_result(self, request_code, result_code, intent):
        if request_code != self._speech_request_code or self._speech_callback is None:
            return
        cb = self._speech_callback
        self._speech_callback = None
        try:
            if intent is None:
                cb(False, 'Konuşma algılama iptal edildi.')
                return
            from jnius import autoclass
            RecognizerIntent = autoclass('android.speech.RecognizerIntent')
            results = intent.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            if results and results.size() > 0:
                text = str(results.get(0))
                Clock.schedule_once(lambda dt: cb(True, text), 0)
            else:
                Clock.schedule_once(lambda dt: cb(False, 'Konuşma anlaşılamadı.'), 0)
        except Exception as exc:
            Clock.schedule_once(lambda dt: cb(False, f'Konuşma algılama hatası: {exc}'), 0)
