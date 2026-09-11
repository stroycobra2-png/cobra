from pathlib import Path
import sqlite3
from datetime import datetime

APP_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = APP_DIR / "data"
DB_PATH = DATA_DIR / "fluentpath.db"

LEVELS = [
    ("A1", "Başlangıç", "Temel kelimeler, selamlaşma ve basit cümleler"),
    ("A2", "Temel", "Günlük yaşam, geçmiş ve gelecek anlatımı"),
    ("B1", "Orta", "Bağımsız iletişim ve daha uzun metinler"),
    ("B2", "Orta-Üst", "Akıcı iletişim, tartışma ve detaylı anlatım"),
    ("C1", "İleri", "Akademik ve profesyonel düzeyde kullanım"),
    ("C2", "Ustalık", "Doğal, nüanslı ve çok ileri düzey kullanım"),
]

SAMPLE_LESSONS = [
    (
        "A1", 1, "Selamlaşma",
        "İlk İngilizce konuşmalarını başlat.",
        "Hello|Merhaba;Hi|Selam;Good morning|Günaydın;Good evening|İyi akşamlar;Goodbye|Hoşça kal",
        "Hello! My name is Alex. Nice to meet you.|Merhaba! Benim adım Alex. Tanıştığıma memnun oldum.",
        "Hello ne demektir?|Merhaba|Teşekkürler|Görüşürüz|Lütfen|0"
    ),
    (
        "A1", 2, "Kendini Tanıtma",
        "Adını, yaşını ve nereden geldiğini söyle.",
        "My name is...|Benim adım...;I am...|Ben...;I am from...|Ben ...'danım;Nice to meet you|Tanıştığıma memnun oldum",
        "My name is Emma. I am a student. I am from London.|Benim adım Emma. Ben bir öğrenciyim. Londra'danım.",
        "I am from Türkiye cümlesinin anlamı nedir?|Türkiye'denim|Türkiye'ye gidiyorum|Türkçe konuşuyorum|Türkiye'yi seviyorum|0"
    ),
    (
        "A1", 3, "Sayılar ve Yaş",
        "1-100 arası sayıları ve yaş söylemeyi öğren.",
        "one|bir;ten|on;twenty|yirmi;hundred|yüz;years old|yaşında",
        "I am sixteen years old.|Ben on altı yaşındayım.",
        "Twenty hangi sayıdır?|2|12|20|200|2"
    ),
]

class Database:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.path = DB_PATH

    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self):
        with self.connect() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS profile (
                id INTEGER PRIMARY KEY CHECK(id = 1),
                name TEXT NOT NULL DEFAULT 'Öğrenci',
                current_level TEXT NOT NULL DEFAULT 'A1',
                xp INTEGER NOT NULL DEFAULT 0,
                daily_goal INTEGER NOT NULL DEFAULT 20
            );

            CREATE TABLE IF NOT EXISTS levels (
                code TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level_code TEXT NOT NULL,
                position INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                vocabulary TEXT NOT NULL,
                example TEXT NOT NULL,
                quiz TEXT NOT NULL,
                UNIQUE(level_code, position)
            );

            CREATE TABLE IF NOT EXISTS lesson_progress (
                lesson_id INTEGER PRIMARY KEY,
                completed INTEGER NOT NULL DEFAULT 0,
                best_score INTEGER NOT NULL DEFAULT 0,
                completed_at TEXT
            );

            CREATE TABLE IF NOT EXISTS study_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity TEXT NOT NULL,
                xp INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );
            """)
            conn.execute(
                "INSERT OR IGNORE INTO profile (id, name, current_level, xp, daily_goal) VALUES (1, 'Öğrenci', 'A1', 0, 20)"
            )
            conn.executemany(
                "INSERT OR IGNORE INTO levels(code,title,description) VALUES (?,?,?)",
                LEVELS
            )
            conn.executemany("""
                INSERT OR IGNORE INTO lessons(
                    level_code, position, title, description, vocabulary, example, quiz
                ) VALUES (?,?,?,?,?,?,?)
            """, SAMPLE_LESSONS)
            conn.commit()

    def get_profile(self):
        with self.connect() as conn:
            return conn.execute("SELECT * FROM profile WHERE id=1").fetchone()

    def update_profile_name(self, name):
        with self.connect() as conn:
            conn.execute("UPDATE profile SET name=? WHERE id=1", (name.strip() or "Öğrenci",))
            conn.commit()

    def get_levels(self):
        with self.connect() as conn:
            return conn.execute("SELECT * FROM levels ORDER BY CASE code WHEN 'A1' THEN 1 WHEN 'A2' THEN 2 WHEN 'B1' THEN 3 WHEN 'B2' THEN 4 WHEN 'C1' THEN 5 ELSE 6 END").fetchall()

    def get_lessons(self, level_code):
        with self.connect() as conn:
            return conn.execute("""
                SELECT l.*, COALESCE(p.completed,0) completed, COALESCE(p.best_score,0) best_score
                FROM lessons l
                LEFT JOIN lesson_progress p ON p.lesson_id=l.id
                WHERE l.level_code=?
                ORDER BY l.position
            """, (level_code,)).fetchall()

    def get_lesson(self, lesson_id):
        with self.connect() as conn:
            return conn.execute("""
                SELECT l.*, COALESCE(p.completed,0) completed, COALESCE(p.best_score,0) best_score
                FROM lessons l
                LEFT JOIN lesson_progress p ON p.lesson_id=l.id
                WHERE l.id=?
            """, (lesson_id,)).fetchone()

    def complete_lesson(self, lesson_id, score):
        with self.connect() as conn:
            old = conn.execute("SELECT completed, best_score FROM lesson_progress WHERE lesson_id=?", (lesson_id,)).fetchone()
            first_completion = old is None or old["completed"] == 0
            best = max(score, old["best_score"] if old else 0)
            conn.execute("""
                INSERT INTO lesson_progress(lesson_id, completed, best_score, completed_at)
                VALUES(?,1,?,?)
                ON CONFLICT(lesson_id) DO UPDATE SET
                    completed=1,
                    best_score=excluded.best_score,
                    completed_at=excluded.completed_at
            """, (lesson_id, best, datetime.now().isoformat(timespec="seconds")))
            earned = 20 if first_completion else 5
            conn.execute("UPDATE profile SET xp=xp+? WHERE id=1", (earned,))
            conn.execute(
                "INSERT INTO study_log(activity,xp,created_at) VALUES(?,?,?)",
                ("Ders tamamlama", earned, datetime.now().isoformat(timespec="seconds"))
            )
            conn.commit()
            return earned

    def progress_stats(self):
        with self.connect() as conn:
            total = conn.execute("SELECT COUNT(*) c FROM lessons").fetchone()["c"]
            completed = conn.execute("SELECT COUNT(*) c FROM lesson_progress WHERE completed=1").fetchone()["c"]
            xp = conn.execute("SELECT xp FROM profile WHERE id=1").fetchone()["xp"]
            return {"total": total, "completed": completed, "xp": xp}
