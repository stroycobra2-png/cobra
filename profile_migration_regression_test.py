import sqlite3
import tempfile
from pathlib import Path

from app.database import Database


def create_real_legacy_db(path):
    c=sqlite3.connect(path)
    c.execute("""CREATE TABLE profile(
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
    )""")
    c.execute("""INSERT INTO profile(
        id,name,current_level,xp,daily_goal,streak,setup_complete,theme,tts_rate
    ) VALUES(1,'Eski Öğretmen','B1',500,30,4,1,'dark',165)""")
    c.commit()
    c.close()


with tempfile.TemporaryDirectory() as td:
    # Gerçek eski DB: profiles tablosu yok -> bir kez migrate edilmeli.
    legacy_path=Path(td)/'legacy.db'
    create_real_legacy_db(legacy_path)
    old=Database(legacy_path)
    assert old._profiles_table_preexisted is False
    old.initialize()
    assert old.has_profiles() is True
    assert old.get_profile()['name']=='Eski Öğretmen'

    # Modern DB: profil oluştur -> son profili sil -> kapat/aç.
    modern_path=Path(td)/'modern.db'
    modern=Database(modern_path)
    modern.initialize()
    pid=modern.create_profile('Silinecek Profil','Öğretmen','A1',20)
    modern.switch_profile(pid)
    assert modern.delete_profile(pid) is False
    assert modern.has_profiles() is False

    # Legacy placeholder satırı hâlâ var; eski bug tam burada tetikleniyordu.
    raw=sqlite3.connect(modern_path)
    legacy_row=raw.execute('SELECT * FROM profile WHERE id=1').fetchone()
    raw.close()
    assert legacy_row is not None

    # Yeniden açınca bu legacy satır artık profile dönüşmemeli.
    modern2=Database(modern_path)
    assert modern2._profiles_table_preexisted is True
    modern2.initialize()
    assert modern2.has_profiles() is False
    assert modern2.profile_count()==0
    assert modern2.active_profile_id() is None
    assert modern2.get_profile() is None

print('Profile migration regression test: PASS')
