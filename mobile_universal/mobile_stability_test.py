import json
import tempfile
from pathlib import Path

from mobile_app.database import Database, LEVEL_ORDER
from mobile_app.curriculum import generate_lessons

# All 300 curriculum records must have valid mobile JSON fields.
lessons = generate_lessons()
assert len(lessons) == 300

for item in lessons:
    vocabulary = json.loads(item['vocabulary'])
    quiz = json.loads(item['quiz'])
    assert isinstance(vocabulary, list) and vocabulary
    assert isinstance(quiz, list) and quiz
    for v in vocabulary:
        assert isinstance(v, dict)
        assert 'word' in v and 'translation' in v
    for q in quiz:
        assert isinstance(q, dict)
        assert isinstance(q.get('options'), list)
        assert 0 <= int(q.get('correct')) < len(q['options'])

with tempfile.TemporaryDirectory() as td:
    path = Path(td) / 'mobile_stable.db'
    db = Database(path)
    db.initialize()
    pid = db.create_profile('Mobil Test', 'Öğretmen', 'A1', 20)
    db.switch_profile(pid)

    assert all(len(db.get_lessons(level)) == 50 for level in LEVEL_ORDER)

    lesson = db.next_lesson()
    assert lesson
    json.loads(lesson['vocabulary'])
    json.loads(lesson['quiz'])

    # Completing a lesson must not crash and should store words.
    earned = db.complete_lesson(lesson['id'], 100)
    assert earned > 0
    assert len(db.all_words()) > 0

print('Mobile stability data test: PASS')
