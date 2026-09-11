from pathlib import Path
from datetime import date, datetime, timedelta
import sqlite3, json, unicodedata
from mobile_app.curriculum import LEVELS, generate_lessons

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / 'data'
DB_PATH = DATA_DIR / 'fluentpath.db'
LEVEL_ORDER = ['A1','A2','B1','B2','C1','C2']
SKILLS = ['vocabulary','grammar','reading','listening','speaking','writing']
ACHIEVEMENTS = [
    ('first_lesson','İlk Adım'),('xp_100','100 XP'),('xp_500','500 XP'),
    ('streak_3','3 Gün Seri'),('streak_7','7 Gün Seri'),('ten_lessons','10 Ders'),('first_review','İlk Tekrar')
]


def normalize_tr_text(value):
    text = unicodedata.normalize('NFC', str(value or ''))
    for broken, fixed in (
        ('İ\u0307', 'İ'), ('I\u0307', 'İ'),
        ('i\u0307', 'i'), ('ı\u0307', 'ı'),
    ):
        text = text.replace(broken, fixed)
    text = text.replace('\u200b', '').replace('\ufeff', '').replace('\u2060', '')
    return unicodedata.normalize('NFC', text)


def _safe_json_list(value):
    try:
        parsed = json.loads(value or '[]')
        return parsed if isinstance(parsed, list) else []
    except (TypeError, ValueError, json.JSONDecodeError):
        return []


class Database:
    def __init__(self, path=None):
        if path is None:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            self.path = DB_PATH
        else:
            self.path = Path(path)
            self.path.parent.mkdir(parents=True, exist_ok=True)

        # Veritabanı dosyasının ve YENİ profil sisteminin bu çalıştırmadan
        # önce var olup olmadığını ayrı ayrı tutuyoruz.
        #
        # Eski sürümlerde `profile`, yeni sürümlerde `profiles` tablosu var.
        # Kullanıcı yeni sistemde son profilini sildiyse yeniden açılışta
        # legacy `profile` kaydı tekrar migrate edilmemelidir.
        self._database_preexisted = self.path.exists() and self.path.stat().st_size > 0
        self._profiles_table_preexisted = False

        if self._database_preexisted:
            try:
                probe = sqlite3.connect(self.path)
                row = probe.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='profiles'"
                ).fetchone()
                self._profiles_table_preexisted = row is not None
                probe.close()
            except sqlite3.Error:
                self._profiles_table_preexisted = False

    def connect(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('PRAGMA busy_timeout=5000')
        return conn

    def initialize(self):
        with self.connect() as conn:
            # Desktop ve mobil sunucu aynı SQLite dosyasını daha güvenli paylaşsın.
            conn.execute('PRAGMA journal_mode=WAL')
            # Legacy schema is kept for backwards compatibility/migration.
            conn.executescript('''
            CREATE TABLE IF NOT EXISTS profile(
                id INTEGER PRIMARY KEY CHECK(id=1),
                name TEXT NOT NULL DEFAULT 'Öğrenci',
                current_level TEXT NOT NULL DEFAULT 'A1',
                xp INTEGER NOT NULL DEFAULT 0,
                daily_goal INTEGER NOT NULL DEFAULT 20,
                streak INTEGER NOT NULL DEFAULT 0,
                last_study_date TEXT,
                setup_complete INTEGER NOT NULL DEFAULT 0,
                theme TEXT NOT NULL DEFAULT 'dark',
                tts_rate INTEGER NOT NULL DEFAULT 165
            );
            CREATE TABLE IF NOT EXISTS levels(
                code TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS lessons(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level_code TEXT NOT NULL,
                unit INTEGER NOT NULL,
                position INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                grammar TEXT NOT NULL,
                vocabulary TEXT NOT NULL,
                example TEXT NOT NULL,
                reading_text TEXT NOT NULL,
                listening_text TEXT NOT NULL,
                speaking_prompt TEXT NOT NULL,
                writing_prompt TEXT NOT NULL,
                quiz TEXT NOT NULL,
                UNIQUE(level_code, position)
            );
            CREATE TABLE IF NOT EXISTS lesson_progress(
                lesson_id INTEGER PRIMARY KEY,
                completed INTEGER NOT NULL DEFAULT 0,
                best_score INTEGER NOT NULL DEFAULT 0,
                attempts INTEGER NOT NULL DEFAULT 0,
                completed_at TEXT
            );
            CREATE TABLE IF NOT EXISTS vocabulary_progress(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level_code TEXT NOT NULL,
                word TEXT NOT NULL,
                translation TEXT NOT NULL,
                example TEXT,
                ease REAL NOT NULL DEFAULT 2.5,
                interval_days INTEGER NOT NULL DEFAULT 0,
                repetitions INTEGER NOT NULL DEFAULT 0,
                due_date TEXT NOT NULL,
                favorite INTEGER NOT NULL DEFAULT 0,
                last_result TEXT,
                UNIQUE(level_code, word)
            );
            CREATE TABLE IF NOT EXISTS study_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity TEXT NOT NULL,
                skill TEXT,
                score INTEGER,
                xp INTEGER NOT NULL DEFAULT 0,
                minutes INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS skill_scores(
                level_code TEXT NOT NULL,
                skill TEXT NOT NULL,
                score REAL NOT NULL DEFAULT 0,
                samples INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(level_code, skill)
            );
            CREATE TABLE IF NOT EXISTS achievements(
                code TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                unlocked INTEGER NOT NULL DEFAULT 0,
                unlocked_at TEXT
            );
            CREATE TABLE IF NOT EXISTS placement_attempts(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                score INTEGER NOT NULL,
                assigned_level TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS profiles(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'Öğretmen',
                current_level TEXT NOT NULL DEFAULT 'A1',
                xp INTEGER NOT NULL DEFAULT 0,
                daily_goal INTEGER NOT NULL DEFAULT 20,
                streak INTEGER NOT NULL DEFAULT 0,
                last_study_date TEXT,
                setup_complete INTEGER NOT NULL DEFAULT 0,
                theme TEXT NOT NULL DEFAULT 'dark',
                tts_rate INTEGER NOT NULL DEFAULT 165,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS app_state(
                id INTEGER PRIMARY KEY CHECK(id=1),
                active_profile_id INTEGER
            );
            CREATE TABLE IF NOT EXISTS lesson_progress_v2(
                profile_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                best_score INTEGER NOT NULL DEFAULT 0,
                attempts INTEGER NOT NULL DEFAULT 0,
                completed_at TEXT,
                PRIMARY KEY(profile_id, lesson_id),
                FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS vocabulary_progress_v2(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                level_code TEXT NOT NULL,
                word TEXT NOT NULL,
                translation TEXT NOT NULL,
                example TEXT,
                ease REAL NOT NULL DEFAULT 2.5,
                interval_days INTEGER NOT NULL DEFAULT 0,
                repetitions INTEGER NOT NULL DEFAULT 0,
                due_date TEXT NOT NULL,
                favorite INTEGER NOT NULL DEFAULT 0,
                last_result TEXT,
                UNIQUE(profile_id, level_code, word),
                FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS study_log_v2(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                activity TEXT NOT NULL,
                skill TEXT,
                score INTEGER,
                xp INTEGER NOT NULL DEFAULT 0,
                minutes INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS skill_scores_v2(
                profile_id INTEGER NOT NULL,
                level_code TEXT NOT NULL,
                skill TEXT NOT NULL,
                score REAL NOT NULL DEFAULT 0,
                samples INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(profile_id, level_code, skill),
                FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS profile_achievements(
                profile_id INTEGER NOT NULL,
                code TEXT NOT NULL,
                title TEXT NOT NULL,
                unlocked INTEGER NOT NULL DEFAULT 0,
                unlocked_at TEXT,
                PRIMARY KEY(profile_id, code),
                FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS placement_attempts_v2(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                assigned_level TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS classes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_profile_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                level_code TEXT NOT NULL DEFAULT 'A1',
                academic_year TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(owner_profile_id) REFERENCES profiles(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS class_lesson_plans(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                planned_date TEXT,
                status TEXT NOT NULL DEFAULT 'Bekliyor',
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(class_id) REFERENCES classes(id) ON DELETE CASCADE
            );
            ''')
            self._ensure_columns(conn, 'profile', {
                'streak':'INTEGER NOT NULL DEFAULT 0','last_study_date':'TEXT',
                'setup_complete':'INTEGER NOT NULL DEFAULT 0','theme':"TEXT NOT NULL DEFAULT 'dark'",
                'tts_rate':'INTEGER NOT NULL DEFAULT 165',
            })
            self._ensure_columns(conn, 'lessons', {
                'unit':'INTEGER NOT NULL DEFAULT 1','grammar':"TEXT NOT NULL DEFAULT ''",
                'reading_text':"TEXT NOT NULL DEFAULT ''",'listening_text':"TEXT NOT NULL DEFAULT ''",
                'speaking_prompt':"TEXT NOT NULL DEFAULT ''",'writing_prompt':"TEXT NOT NULL DEFAULT ''",
            })
            self._ensure_columns(conn, 'lesson_progress', {'attempts':'INTEGER NOT NULL DEFAULT 0'})
            self._ensure_columns(conn, 'study_log', {'skill':'TEXT','score':'INTEGER','minutes':'INTEGER NOT NULL DEFAULT 0'})

            conn.execute('INSERT OR IGNORE INTO profile(id) VALUES(1)')
            conn.executemany('INSERT OR IGNORE INTO levels(code,title,description) VALUES(?,?,?)', LEVELS)
            for item in generate_lessons():
                conn.execute('''INSERT INTO lessons(
                    level_code,unit,position,title,description,grammar,vocabulary,example,
                    reading_text,listening_text,speaking_prompt,writing_prompt,quiz
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(level_code,position) DO UPDATE SET
                    unit=excluded.unit,title=excluded.title,description=excluded.description,
                    grammar=excluded.grammar,vocabulary=excluded.vocabulary,example=excluded.example,
                    reading_text=excluded.reading_text,listening_text=excluded.listening_text,
                    speaking_prompt=excluded.speaking_prompt,writing_prompt=excluded.writing_prompt,
                    quiz=excluded.quiz''', (
                    item['level_code'],item['unit'],item['position'],item['title'],item['description'],
                    item['grammar'],item['vocabulary'],item['example'],item['reading_text'],
                    item['listening_text'],item['speaking_prompt'],item['writing_prompt'],item['quiz']))
            for code,title in ACHIEVEMENTS:
                conn.execute('INSERT OR IGNORE INTO achievements(code,title) VALUES(?,?)',(code,title))

            self._migrate_profiles(conn)
            self._normalize_existing_mobile_text(conn)
            conn.commit()

    def _normalize_existing_mobile_text(self, conn):
        """Repair decomposed/zero-width text created by older mobile keyboards."""
        table_columns = {
            'profile': ['name'],
            'profiles': ['name', 'role'],
            'classes': ['name', 'academic_year', 'notes'],
            'class_lesson_plans': ['status', 'notes'],
            'vocabulary_progress': ['word', 'translation', 'example', 'last_result'],
            'vocabulary_progress_v2': ['word', 'translation', 'example', 'last_result'],
        }
        for table, columns in table_columns.items():
            try:
                info = conn.execute(f'PRAGMA table_info({table})').fetchall()
                available = {r['name'] for r in info}
                pk_cols = [r['name'] for r in info if r['pk']]
                if not pk_cols:
                    continue
                pk = pk_cols[0]
                usable = [c for c in columns if c in available]
                if not usable:
                    continue
                rows = conn.execute(f"SELECT {pk}," + ','.join(usable) + f" FROM {table}").fetchall()
                for row in rows:
                    changes = {}
                    for col in usable:
                        if row[col] is None:
                            continue
                        cleaned = normalize_tr_text(row[col])
                        if cleaned != row[col]:
                            changes[col] = cleaned
                    if changes:
                        clause = ','.join(f'{c}=?' for c in changes)
                        conn.execute(f'UPDATE {table} SET {clause} WHERE {pk}=?', tuple(changes.values()) + (row[pk],))
            except sqlite3.Error:
                continue

    def _ensure_columns(self, conn, table, columns):
        existing={row['name'] for row in conn.execute(f'PRAGMA table_info({table})').fetchall()}
        for name,definition in columns.items():
            if name not in existing:
                conn.execute(f'ALTER TABLE {table} ADD COLUMN {name} {definition}')

    def _migrate_profiles(self, conn):
        # Eski sürüm verilerini yalnızca gerçekten eski bir veritabanı varsa taşı.
        # Temiz kurulumda profiles tablosu bilinçli olarak boş kalır.
        count = conn.execute('SELECT COUNT(*) n FROM profiles').fetchone()['n']

        if (
            count == 0
            and self._database_preexisted
            and not self._profiles_table_preexisted
        ):
            legacy = conn.execute('SELECT * FROM profile WHERE id=1').fetchone()
            if legacy:
                now = datetime.now().isoformat(timespec='seconds')
                conn.execute('''INSERT INTO profiles(
                    name,role,current_level,xp,daily_goal,streak,last_study_date,
                    setup_complete,theme,tts_rate,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?)''',(
                    (legacy['name'] or 'Öğretmen'),
                    'Öğretmen',
                    legacy['current_level'] or 'A1',
                    legacy['xp'] or 0,
                    legacy['daily_goal'] or 20,
                    legacy['streak'] or 0,
                    legacy['last_study_date'],
                    1 if legacy['setup_complete'] else 0,
                    legacy['theme'] or 'dark',
                    legacy['tts_rate'] or 165,
                    now
                ))

        count = conn.execute('SELECT COUNT(*) n FROM profiles').fetchone()['n']
        conn.execute('INSERT OR IGNORE INTO app_state(id,active_profile_id) VALUES(1,NULL)')

        if count == 0:
            # `profiles` sistemi daha önce mevcutsa bu, kullanıcının bütün
            # profilleri bilerek silmiş olduğu geçerli bir 0-profil durumudur.
            # Legacy `profile` kaydını burada asla yeniden diriltme.
            conn.execute('UPDATE app_state SET active_profile_id=NULL WHERE id=1')
            return

        pid = conn.execute('SELECT id FROM profiles ORDER BY id LIMIT 1').fetchone()['id']
        active = conn.execute('SELECT active_profile_id FROM app_state WHERE id=1').fetchone()

        if (
            not active
            or active['active_profile_id'] is None
            or not conn.execute(
                'SELECT 1 FROM profiles WHERE id=?',
                (active['active_profile_id'],)
            ).fetchone()
        ):
            conn.execute('UPDATE app_state SET active_profile_id=? WHERE id=1',(pid,))

        if conn.execute('SELECT COUNT(*) n FROM lesson_progress_v2').fetchone()['n']==0:
            conn.execute('''INSERT OR IGNORE INTO lesson_progress_v2(
                profile_id,lesson_id,completed,best_score,attempts,completed_at
            )
                SELECT ?,lesson_id,completed,best_score,attempts,completed_at
                FROM lesson_progress''',(pid,))

        if conn.execute('SELECT COUNT(*) n FROM vocabulary_progress_v2').fetchone()['n']==0:
            conn.execute('''INSERT OR IGNORE INTO vocabulary_progress_v2(
                profile_id,level_code,word,translation,example,ease,interval_days,
                repetitions,due_date,favorite,last_result
            )
                SELECT ?,level_code,word,translation,example,ease,interval_days,
                repetitions,due_date,favorite,last_result
                FROM vocabulary_progress''',(pid,))

        if conn.execute('SELECT COUNT(*) n FROM study_log_v2').fetchone()['n']==0:
            conn.execute('''INSERT INTO study_log_v2(
                profile_id,activity,skill,score,xp,minutes,created_at
            )
                SELECT ?,activity,skill,score,xp,minutes,created_at
                FROM study_log''',(pid,))

        if conn.execute('SELECT COUNT(*) n FROM skill_scores_v2').fetchone()['n']==0:
            conn.execute('''INSERT OR IGNORE INTO skill_scores_v2(
                profile_id,level_code,skill,score,samples
            )
                SELECT ?,level_code,skill,score,samples
                FROM skill_scores''',(pid,))

        if conn.execute('SELECT COUNT(*) n FROM profile_achievements').fetchone()['n']==0:
            old={r['code']:r for r in conn.execute('SELECT * FROM achievements').fetchall()}
            for code,title in ACHIEVEMENTS:
                row=old.get(code)
                conn.execute(
                    'INSERT OR IGNORE INTO profile_achievements(profile_id,code,title,unlocked,unlocked_at) VALUES(?,?,?,?,?)',
                    (pid,code,title,row['unlocked'] if row else 0,row['unlocked_at'] if row else None)
                )

        if conn.execute('SELECT COUNT(*) n FROM placement_attempts_v2').fetchone()['n']==0:
            conn.execute('''INSERT INTO placement_attempts_v2(
                profile_id,score,assigned_level,created_at
            )
                SELECT ?,score,assigned_level,created_at
                FROM placement_attempts''',(pid,))

        for profile in conn.execute('SELECT id FROM profiles').fetchall():
            for code,title in ACHIEVEMENTS:
                conn.execute(
                    'INSERT OR IGNORE INTO profile_achievements(profile_id,code,title) VALUES(?,?,?)',
                    (profile['id'],code,title)
                )

    def has_profiles(self):
        with self.connect() as c:
            return c.execute('SELECT COUNT(*) n FROM profiles').fetchone()['n'] > 0

    def profile_count(self):
        with self.connect() as c:
            return c.execute('SELECT COUNT(*) n FROM profiles').fetchone()['n']

    def active_profile_id(self):
        with self.connect() as c:
            row=c.execute('SELECT active_profile_id FROM app_state WHERE id=1').fetchone()
            if not row or row['active_profile_id'] is None:
                return None
            return row['active_profile_id']

    def get_profile(self):
        with self.connect() as c:
            state=c.execute('SELECT active_profile_id FROM app_state WHERE id=1').fetchone()
            if not state or state['active_profile_id'] is None:
                return None
            return c.execute(
                'SELECT * FROM profiles WHERE id=?',
                (state['active_profile_id'],)
            ).fetchone()

    def list_profiles(self):
        with self.connect() as c:
            state=c.execute('SELECT active_profile_id FROM app_state WHERE id=1').fetchone()
            active=state['active_profile_id'] if state else None
            return c.execute('''SELECT p.*, CASE WHEN p.id=? THEN 1 ELSE 0 END AS active
                FROM profiles p ORDER BY active DESC, name COLLATE NOCASE''',(active,)).fetchall()

    def create_profile(self, name, role='Öğretmen', level='A1', daily_goal=20):
        name=normalize_tr_text(name).strip()
        if not name:
            raise ValueError('Profil adı boş olamaz.')
        if role not in ('Öğretmen','Öğrenci'):
            role='Öğretmen'
        if level not in LEVEL_ORDER:
            level='A1'

        current=self.get_profile()
        theme=current['theme'] if current else 'dark'
        tts_rate=current['tts_rate'] if current else 165

        with self.connect() as c:
            cur=c.execute('''INSERT INTO profiles(
                name,role,current_level,daily_goal,setup_complete,theme,tts_rate,created_at
            ) VALUES(?,?,?,?,1,?,?,?)''',(
                name,role,level,int(daily_goal),theme,tts_rate,
                datetime.now().isoformat(timespec='seconds')
            ))
            pid=cur.lastrowid

            for code,title in ACHIEVEMENTS:
                c.execute(
                    'INSERT INTO profile_achievements(profile_id,code,title) VALUES(?,?,?)',
                    (pid,code,title)
                )

            c.execute('INSERT OR IGNORE INTO app_state(id,active_profile_id) VALUES(1,NULL)')
            state=c.execute('SELECT active_profile_id FROM app_state WHERE id=1').fetchone()
            if not state or state['active_profile_id'] is None:
                c.execute('UPDATE app_state SET active_profile_id=? WHERE id=1',(pid,))

            c.commit()
            return pid

    def switch_profile(self, profile_id):
        with self.connect() as c:
            if not c.execute('SELECT 1 FROM profiles WHERE id=?',(profile_id,)).fetchone():
                raise ValueError('Profil bulunamadı.')
            c.execute('INSERT OR IGNORE INTO app_state(id,active_profile_id) VALUES(1,NULL)')
            c.execute('UPDATE app_state SET active_profile_id=? WHERE id=1',(profile_id,))
            c.commit()

    def delete_profile(self, profile_id):
        with self.connect() as c:
            if not c.execute('SELECT 1 FROM profiles WHERE id=?',(profile_id,)).fetchone():
                raise ValueError('Profil bulunamadı.')

            c.execute('INSERT OR IGNORE INTO app_state(id,active_profile_id) VALUES(1,NULL)')
            state=c.execute('SELECT active_profile_id FROM app_state WHERE id=1').fetchone()
            active=state['active_profile_id'] if state else None

            # profile_id ile ilişkili ders, kelime, istatistik ve sınıf verileri
            # ON DELETE CASCADE sayesinde birlikte temizlenir.
            c.execute('DELETE FROM profiles WHERE id=?',(profile_id,))

            remaining=c.execute('SELECT id FROM profiles ORDER BY id LIMIT 1').fetchone()

            if active==profile_id:
                c.execute(
                    'UPDATE app_state SET active_profile_id=? WHERE id=1',
                    (remaining['id'] if remaining else None,)
                )
            elif remaining is None:
                c.execute('UPDATE app_state SET active_profile_id=NULL WHERE id=1')

            c.commit()
            return remaining is not None

    def set_setup(self, name, level='A1', daily_goal=20):
        pid=self.active_profile_id()
        with self.connect() as c:
            c.execute('UPDATE profiles SET name=?,current_level=?,daily_goal=?,setup_complete=1 WHERE id=?',
                      (normalize_tr_text(name).strip() or 'Öğrenci',level,daily_goal,pid))
            c.commit()

    def update_profile(self, name=None, daily_goal=None, theme=None, tts_rate=None, role=None):
        fields=[]; vals=[]
        for k,v in [('name',name),('daily_goal',daily_goal),('theme',theme),('tts_rate',tts_rate),('role',role)]:
            if v is not None:
                if k in ('name','role','theme'): v=normalize_tr_text(v)
                fields.append(f'{k}=?'); vals.append(v)
        if not fields: return
        vals.append(self.active_profile_id())
        with self.connect() as c:
            c.execute('UPDATE profiles SET '+','.join(fields)+' WHERE id=?', vals)
            c.commit()

    def get_levels(self):
        with self.connect() as c: rows=c.execute('SELECT * FROM levels').fetchall()
        return sorted(rows,key=lambda r:LEVEL_ORDER.index(r['code']))

    def level_accessible(self, code):
        current=self.get_profile()['current_level']
        return LEVEL_ORDER.index(code)<=LEVEL_ORDER.index(current)

    def get_lessons(self, level):
        pid=self.active_profile_id()
        with self.connect() as c:
            return c.execute('''SELECT l.*,COALESCE(p.completed,0) completed,COALESCE(p.best_score,0) best_score,
                COALESCE(p.attempts,0) attempts FROM lessons l
                LEFT JOIN lesson_progress_v2 p ON p.lesson_id=l.id AND p.profile_id=?
                WHERE l.level_code=? ORDER BY l.position''',(pid,level)).fetchall()

    def get_lesson(self, lesson_id):
        pid=self.active_profile_id()
        with self.connect() as c:
            return c.execute('''SELECT l.*,COALESCE(p.completed,0) completed,COALESCE(p.best_score,0) best_score,
                COALESCE(p.attempts,0) attempts FROM lessons l
                LEFT JOIN lesson_progress_v2 p ON p.lesson_id=l.id AND p.profile_id=? WHERE l.id=?''',(pid,lesson_id)).fetchone()

    def lesson_accessible(self, lesson_id):
        lesson=self.get_lesson(lesson_id)
        if not lesson or not self.level_accessible(lesson['level_code']): return False
        if lesson['position']==1: return True
        lessons=self.get_lessons(lesson['level_code'])
        prev=next((x for x in lessons if x['position']==lesson['position']-1),None)
        return bool(prev and prev['completed'])

    def _touch_streak(self, conn, pid=None):
        pid=pid or self.active_profile_id()
        p=conn.execute('SELECT streak,last_study_date FROM profiles WHERE id=?',(pid,)).fetchone()
        today=date.today(); last=date.fromisoformat(p['last_study_date']) if p['last_study_date'] else None; streak=p['streak']
        if last==today: return
        streak=streak+1 if last==today-timedelta(days=1) else 1
        conn.execute('UPDATE profiles SET streak=?,last_study_date=? WHERE id=?',(streak,today.isoformat(),pid))

    def log_activity(self, activity, skill=None, score=None, xp=0, minutes=1):
        pid=self.active_profile_id()
        with self.connect() as c:
            self._touch_streak(c,pid)
            c.execute('INSERT INTO study_log_v2(profile_id,activity,skill,score,xp,minutes,created_at) VALUES(?,?,?,?,?,?,?)',
                      (pid,activity,skill,score,xp,minutes,datetime.now().isoformat(timespec='seconds')))
            if xp: c.execute('UPDATE profiles SET xp=xp+? WHERE id=?',(xp,pid))
            if skill and score is not None:
                level=c.execute('SELECT current_level FROM profiles WHERE id=?',(pid,)).fetchone()['current_level']
                old=c.execute('SELECT score,samples FROM skill_scores_v2 WHERE profile_id=? AND level_code=? AND skill=?',(pid,level,skill)).fetchone()
                if old:
                    n=old['samples']+1; avg=(old['score']*old['samples']+score)/n
                    c.execute('UPDATE skill_scores_v2 SET score=?,samples=? WHERE profile_id=? AND level_code=? AND skill=?',(avg,n,pid,level,skill))
                else:
                    c.execute('INSERT INTO skill_scores_v2(profile_id,level_code,skill,score,samples) VALUES(?,?,?,?,1)',(pid,level,skill,score))
            c.commit()
        self.refresh_achievements()

    def complete_lesson(self, lesson_id, score):
        pid=self.active_profile_id(); lesson=self.get_lesson(lesson_id)
        if not lesson: return 0
        first=not bool(lesson['completed']); earned=30 if first else 8
        with self.connect() as c:
            c.execute('''INSERT INTO lesson_progress_v2(profile_id,lesson_id,completed,best_score,attempts,completed_at)
                VALUES(?,?,1,?,1,?) ON CONFLICT(profile_id,lesson_id) DO UPDATE SET
                completed=1,best_score=MAX(best_score,excluded.best_score),attempts=attempts+1,completed_at=excluded.completed_at''',
                (pid,lesson_id,score,datetime.now().isoformat(timespec='seconds')))
            for v in _safe_json_list(lesson['vocabulary']):
                c.execute('''INSERT OR IGNORE INTO vocabulary_progress_v2(profile_id,level_code,word,translation,example,due_date)
                    VALUES(?,?,?,?,?,?)''',(pid,lesson['level_code'],v['word'],v['translation'],v.get('example',''),date.today().isoformat()))
            self._touch_streak(c,pid)
            c.execute('UPDATE profiles SET xp=xp+? WHERE id=?',(earned,pid))
            c.execute('INSERT INTO study_log_v2(profile_id,activity,skill,score,xp,minutes,created_at) VALUES(?,?,?,?,?,?,?)',
                      (pid,f"Ders: {lesson['title']}",'grammar',score,earned,8,datetime.now().isoformat(timespec='seconds')))
            c.commit()
        self._maybe_advance_level(lesson['level_code']); self.refresh_achievements(); return earned

    def _maybe_advance_level(self, level):
        pid=self.active_profile_id(); lessons=self.get_lessons(level)
        if lessons and all(x['completed'] for x in lessons):
            idx=LEVEL_ORDER.index(level)
            if idx<len(LEVEL_ORDER)-1:
                with self.connect() as c:
                    current=c.execute('SELECT current_level FROM profiles WHERE id=?',(pid,)).fetchone()['current_level']
                    if current==level:
                        c.execute('UPDATE profiles SET current_level=? WHERE id=?',(LEVEL_ORDER[idx+1],pid)); c.commit()

    def save_placement(self, score, level):
        pid=self.active_profile_id()
        with self.connect() as c:
            c.execute('INSERT INTO placement_attempts_v2(profile_id,score,assigned_level,created_at) VALUES(?,?,?,?)',
                      (pid,score,level,datetime.now().isoformat(timespec='seconds')))
            c.execute('UPDATE profiles SET current_level=?,setup_complete=1 WHERE id=?',(level,pid)); c.commit()

    def due_words(self, limit=50):
        pid=self.active_profile_id()
        with self.connect() as c:
            return c.execute('SELECT * FROM vocabulary_progress_v2 WHERE profile_id=? AND due_date<=? ORDER BY due_date,id LIMIT ?',
                             (pid,date.today().isoformat(),limit)).fetchall()

    def all_words(self):
        pid=self.active_profile_id()
        with self.connect() as c:
            return c.execute('SELECT * FROM vocabulary_progress_v2 WHERE profile_id=? ORDER BY level_code,word',(pid,)).fetchall()

    def review_word(self, word_id, quality):
        pid=self.active_profile_id()
        with self.connect() as c:
            row=c.execute('SELECT * FROM vocabulary_progress_v2 WHERE id=? AND profile_id=?',(word_id,pid)).fetchone()
            if not row: return
            reps=row['repetitions']; ease=row['ease']; interval=row['interval_days']
            if quality=='hard': reps=0; interval=1; ease=max(1.3,ease-0.2)
            elif quality=='medium': reps+=1; interval=1 if reps==1 else max(2,int(max(1,interval)*ease*0.7))
            else:
                reps+=1; interval=1 if reps==1 else 3 if reps==2 else max(4,int(max(1,interval)*ease)); ease=min(3.0,ease+0.1)
            due=date.today()+timedelta(days=interval)
            c.execute('UPDATE vocabulary_progress_v2 SET repetitions=?,interval_days=?,ease=?,due_date=?,last_result=? WHERE id=? AND profile_id=?',
                      (reps,interval,ease,due.isoformat(),quality,word_id,pid))
            self._touch_streak(c,pid); c.execute('UPDATE profiles SET xp=xp+5 WHERE id=?',(pid,))
            c.execute('INSERT INTO study_log_v2(profile_id,activity,skill,score,xp,minutes,created_at) VALUES(?,?,?,?,?,?,?)',
                      (pid,'Kelime tekrarı','vocabulary',100 if quality=='easy' else 70 if quality=='medium' else 40,5,1,datetime.now().isoformat(timespec='seconds')))
            c.commit()
        self.refresh_achievements()

    def toggle_favorite(self, word_id):
        pid=self.active_profile_id()
        with self.connect() as c:
            c.execute('UPDATE vocabulary_progress_v2 SET favorite=CASE favorite WHEN 1 THEN 0 ELSE 1 END WHERE id=? AND profile_id=?',(word_id,pid)); c.commit()

    def skill_scores(self, level=None):
        pid=self.active_profile_id(); level=level or self.get_profile()['current_level']
        with self.connect() as c: rows=c.execute('SELECT * FROM skill_scores_v2 WHERE profile_id=? AND level_code=?',(pid,level)).fetchall()
        d={s:0 for s in SKILLS}
        for r in rows: d[r['skill']]=round(r['score'])
        return d

    def stats(self):
        pid=self.active_profile_id()
        with self.connect() as c:
            total=c.execute('SELECT COUNT(*) n FROM lessons').fetchone()['n']
            completed=c.execute('SELECT COUNT(*) n FROM lesson_progress_v2 WHERE profile_id=? AND completed=1',(pid,)).fetchone()['n']
            words=c.execute('SELECT COUNT(*) n FROM vocabulary_progress_v2 WHERE profile_id=?',(pid,)).fetchone()['n']
            reviews=c.execute("SELECT COUNT(*) n FROM study_log_v2 WHERE profile_id=? AND activity='Kelime tekrarı'",(pid,)).fetchone()['n']
            minutes=c.execute('SELECT COALESCE(SUM(minutes),0) n FROM study_log_v2 WHERE profile_id=?',(pid,)).fetchone()['n']
        p=self.get_profile(); return {'total':total,'completed':completed,'words':words,'reviews':reviews,'minutes':minutes,'xp':p['xp'],'streak':p['streak']}

    def today_minutes(self):
        pid=self.active_profile_id(); prefix=date.today().isoformat()+'%'
        with self.connect() as c:
            return c.execute('SELECT COALESCE(SUM(minutes),0) n FROM study_log_v2 WHERE profile_id=? AND created_at LIKE ?',(pid,prefix)).fetchone()['n']

    def next_lesson(self):
        level=self.get_profile()['current_level']
        for lesson in self.get_lessons(level):
            if not lesson['completed'] and self.lesson_accessible(lesson['id']): return lesson
        return None

    def recent_activities(self, limit=6):
        pid=self.active_profile_id()
        with self.connect() as c:
            return c.execute('SELECT * FROM study_log_v2 WHERE profile_id=? ORDER BY id DESC LIMIT ?',(pid,limit)).fetchall()

    def today_summary(self):
        pid=self.active_profile_id(); prefix=date.today().isoformat()+'%'
        with self.connect() as c:
            row=c.execute('SELECT COUNT(*) activities,COALESCE(SUM(xp),0) xp,COALESCE(SUM(minutes),0) minutes FROM study_log_v2 WHERE profile_id=? AND created_at LIKE ?',(pid,prefix)).fetchone()
        return {'activities':row['activities'],'xp':row['xp'],'minutes':row['minutes']}

    def current_level_progress(self):
        level=self.get_profile()['current_level']; lessons=self.get_lessons(level); completed=sum(1 for x in lessons if x['completed']); total=len(lessons)
        return {'level':level,'completed':completed,'total':total,'percent':round(completed/max(1,total)*100)}

    def weekly_minutes(self):
        pid=self.active_profile_id(); result=[]; labels=['Pzt','Sal','Çar','Per','Cum','Cmt','Paz']
        with self.connect() as c:
            for offset in range(6,-1,-1):
                day=date.today()-timedelta(days=offset); prefix=day.isoformat()+'%'
                minutes=c.execute('SELECT COALESCE(SUM(minutes),0) n FROM study_log_v2 WHERE profile_id=? AND created_at LIKE ?',(pid,prefix)).fetchone()['n']
                result.append({'date':day.isoformat(),'label':labels[day.weekday()],'minutes':minutes})
        return result

    def refresh_achievements(self):
        pid=self.active_profile_id(); s=self.stats(); unlock=[]
        if s['completed']>=1: unlock.append('first_lesson')
        if s['completed']>=10: unlock.append('ten_lessons')
        if s['xp']>=100: unlock.append('xp_100')
        if s['xp']>=500: unlock.append('xp_500')
        if s['streak']>=3: unlock.append('streak_3')
        if s['streak']>=7: unlock.append('streak_7')
        if s['reviews']>=1: unlock.append('first_review')
        if unlock:
            with self.connect() as c:
                for code in unlock:
                    c.execute('UPDATE profile_achievements SET unlocked=1,unlocked_at=COALESCE(unlocked_at,?) WHERE profile_id=? AND code=?',
                              (datetime.now().isoformat(timespec='seconds'),pid,code))
                c.commit()

    def achievements(self):
        self.refresh_achievements(); pid=self.active_profile_id()
        with self.connect() as c:
            return c.execute('SELECT * FROM profile_achievements WHERE profile_id=? ORDER BY unlocked DESC,title',(pid,)).fetchall()

    # ---------------- Teacher / class management ----------------
    def create_class(self, name, level_code='A1', academic_year='', notes=''):
        name=normalize_tr_text(name).strip()
        if not name: raise ValueError('Sınıf adı boş olamaz.')
        if level_code not in LEVEL_ORDER: level_code='A1'
        pid=self.active_profile_id()
        with self.connect() as c:
            cur=c.execute('''INSERT INTO classes(owner_profile_id,name,level_code,academic_year,notes,created_at)
                VALUES(?,?,?,?,?,?)''',(pid,name,level_code,normalize_tr_text(academic_year).strip(),normalize_tr_text(notes).strip(),datetime.now().isoformat(timespec='seconds')))
            c.commit(); return cur.lastrowid

    def list_classes(self):
        pid=self.active_profile_id()
        with self.connect() as c:
            return c.execute('''SELECT c.*,
                (SELECT COUNT(*) FROM class_lesson_plans p WHERE p.class_id=c.id) plan_count,
                (SELECT COUNT(*) FROM class_lesson_plans p WHERE p.class_id=c.id AND p.status='İşlendi') done_count
                FROM classes c WHERE c.owner_profile_id=? ORDER BY c.name COLLATE NOCASE''',(pid,)).fetchall()

    def get_class(self, class_id):
        pid=self.active_profile_id()
        with self.connect() as c:
            return c.execute('SELECT * FROM classes WHERE id=? AND owner_profile_id=?',(class_id,pid)).fetchone()

    def delete_class(self, class_id):
        pid=self.active_profile_id()
        with self.connect() as c:
            c.execute('DELETE FROM classes WHERE id=? AND owner_profile_id=?',(class_id,pid)); c.commit()

    def add_class_plan(self, class_id, lesson_id, planned_date='', notes=''):
        if not self.get_class(class_id): raise ValueError('Sınıf bulunamadı.')
        if not self.get_lesson(lesson_id): raise ValueError('Ders bulunamadı.')
        with self.connect() as c:
            cur=c.execute('''INSERT INTO class_lesson_plans(class_id,lesson_id,planned_date,status,notes,created_at)
                VALUES(?,?,?,'Bekliyor',?,?)''',(class_id,lesson_id,normalize_tr_text(planned_date).strip(),normalize_tr_text(notes).strip(),datetime.now().isoformat(timespec='seconds')))
            c.commit(); return cur.lastrowid

    def list_class_plans(self, class_id):
        if not self.get_class(class_id): return []
        with self.connect() as c:
            return c.execute('''SELECT p.*,l.level_code,l.unit,l.position,l.title lesson_title
                FROM class_lesson_plans p JOIN lessons l ON l.id=p.lesson_id
                WHERE p.class_id=? ORDER BY CASE WHEN p.planned_date='' THEN 1 ELSE 0 END,p.planned_date,p.id''',(class_id,)).fetchall()

    def set_class_plan_status(self, plan_id, status):
        status='İşlendi' if status=='İşlendi' else 'Bekliyor'; pid=self.active_profile_id()
        with self.connect() as c:
            c.execute('''UPDATE class_lesson_plans SET status=? WHERE id=? AND class_id IN
                (SELECT id FROM classes WHERE owner_profile_id=?)''',(status,plan_id,pid)); c.commit()

    def delete_class_plan(self, plan_id):
        pid=self.active_profile_id()
        with self.connect() as c:
            c.execute('''DELETE FROM class_lesson_plans WHERE id=? AND class_id IN
                (SELECT id FROM classes WHERE owner_profile_id=?)''',(plan_id,pid)); c.commit()

    def next_class_plan(self, class_id):
        plans=self.list_class_plans(class_id)
        return next((p for p in plans if p['status']!='İşlendi'),None)
