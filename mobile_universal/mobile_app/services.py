import re
from difflib import SequenceMatcher


def normalize(text):
    return re.sub(r'[^a-z0-9 ]+', '', (text or '').lower()).strip()


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
    words = [w for w in re.findall(r"[A-Za-z']+", text or '')]
    minimum = {'A1': 20, 'A2': 25, 'B1': 50, 'B2': 60, 'C1': 90, 'C2': 100}.get(level, 30)
    if not words:
        return 0, ['Metin boş.']
    score = 0
    notes = []
    score += min(35, round(len(words) / minimum * 35))
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
