import re
from difflib import SequenceMatcher


class SpeechService:
    """Text-to-speech and microphone speech recognition helper.

    Microphone capture deliberately uses sounddevice instead of
    speech_recognition.Microphone/PyAudio. This avoids the common PyAudio
    installation problem on Windows/Python 3.12.
    """

    def __init__(self, rate=165, record_seconds=7, sample_rate=16000):
        self.rate = rate
        self.record_seconds = record_seconds
        self.sample_rate = sample_rate

    def speak(self, text):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', self.rate)
            engine.say(text)
            engine.runAndWait()
            return True, 'Seslendirildi.'
        except Exception as e:
            return False, f'Seslendirme kullanılamıyor: {e}'

    def microphone_info(self):
        """Return a human-readable default microphone summary."""
        try:
            import sounddevice as sd
            default_in = sd.default.device[0]
            if default_in is None or int(default_in) < 0:
                return False, 'Windows üzerinde varsayılan bir mikrofon seçili değil.'
            info = sd.query_devices(int(default_in), 'input')
            return True, f"{info['name']}"
        except Exception as e:
            return False, f'Mikrofon bilgisi alınamadı: {e}'

    def listen_once(self):
        """Record a short phrase from the default microphone and recognize English.

        Capture: sounddevice + NumPy
        Recognition: SpeechRecognition AudioData + Google recognizer
        No PyAudio is used.
        """
        try:
            import numpy as np
            import sounddevice as sd
            import speech_recognition as sr
        except ImportError as e:
            return False, (
                'Mikrofon bileşenlerinden biri eksik. KURULUM.bat dosyasını yeniden '
                f'çalıştır. Eksik paket: {getattr(e, "name", str(e))}'
            )

        try:
            default_in = sd.default.device[0]
            if default_in is None or int(default_in) < 0:
                return False, (
                    'Windows üzerinde varsayılan mikrofon bulunamadı. '
                    'Ayarlar > Sistem > Ses > Giriş bölümünden mikrofonunu seç.'
                )

            # Validate the selected input device before recording.
            sd.check_input_settings(
                device=int(default_in),
                channels=1,
                samplerate=self.sample_rate,
                dtype='int16',
            )

            frames = int(self.record_seconds * self.sample_rate)
            recording = sd.rec(
                frames,
                samplerate=self.sample_rate,
                channels=1,
                dtype='int16',
                device=int(default_in),
                blocking=True,
            )

            if recording is None or recording.size == 0:
                return False, 'Mikrofondan ses verisi alınamadı.'

            # Detect near-silence so the user gets a useful message instead of a
            # generic recognizer error.
            peak = int(np.max(np.abs(recording.astype(np.int32))))
            if peak < 180:
                return False, (
                    'Mikrofon açık ancak belirgin bir ses algılanmadı. '
                    'Mikrofona biraz daha yakın konuşup tekrar dene.'
                )

            recognizer = sr.Recognizer()
            audio = sr.AudioData(recording.tobytes(), self.sample_rate, 2)

            try:
                text = recognizer.recognize_google(audio, language='en-US')
            except sr.UnknownValueError:
                return False, (
                    'Ses kaydı alındı fakat konuşma anlaşılamadı. '
                    'Cümleyi daha net ve biraz daha yavaş söyleyip tekrar dene.'
                )
            except sr.RequestError as e:
                return False, (
                    'Mikrofon çalışıyor fakat konuşmayı yazıya çevirme servisine '
                    f'ulaşılamadı. İnternet bağlantını kontrol et. ({e})'
                )

            text = (text or '').strip()
            if not text:
                return False, 'Ses kaydı alındı fakat metin üretilemedi.'
            return True, text

        except Exception as e:
            # sounddevice.PortAudioError and Windows device errors land here.
            return False, (
                'Mikrofon kaydı başlatılamadı. Windows mikrofon iznini ve varsayılan '
                f'giriş aygıtını kontrol et. ({type(e).__name__}: {e})'
            )


def normalize(text):
    return re.sub(r'[^a-z0-9 ]+', '', text.lower()).strip()


def speaking_score(target, spoken):
    a = normalize(target)
    b = normalize(spoken)
    if not b:
        return 0
    similarity = SequenceMatcher(None, a, b).ratio()
    target_words = set(a.split())
    spoken_words = set(b.split())
    coverage = len(target_words & spoken_words) / max(1, len(target_words))
    return round((similarity * 0.65 + coverage * 0.35) * 100)


def writing_score(text, level='A1'):
    words = [w for w in re.findall(r"[A-Za-z']+", text)]
    minimum = {'A1': 20, 'A2': 25, 'B1': 50, 'B2': 60, 'C1': 90, 'C2': 100}.get(level, 30)
    if not words:
        return 0, ['Metin boş.']
    score = 0
    notes = []
    length = min(35, round(len(words) / minimum * 35))
    score += length
    if len(words) >= minimum:
        notes.append('✓ Hedef kelime sayısına ulaştın.')
    else:
        notes.append(f'• En az {minimum} kelime hedefle. Şu an {len(words)} kelime.')
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    if len(sentences) >= 2:
        score += 20
        notes.append('✓ Birden fazla cümle kullandın.')
    else:
        notes.append('• Fikrini birkaç cümleye böl.')
    if text.strip()[:1].isupper():
        score += 10
    else:
        notes.append('• Cümleye büyük harfle başla.')
    if text.strip().endswith(('.', '!', '?')):
        score += 10
    else:
        notes.append('• Sonuna uygun noktalama işareti ekle.')
    unique = len(set(w.lower() for w in words)) / max(1, len(words))
    score += round(min(15, unique * 20))
    connectors = ['and', 'but', 'because', 'however', 'although', 'therefore', 'while', 'if', 'when']
    if any(c in [w.lower() for w in words] for c in connectors):
        score += 10
        notes.append('✓ Bağlayıcı ifade kullandın.')
    return min(100, score), notes
