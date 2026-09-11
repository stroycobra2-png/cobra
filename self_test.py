from pathlib import Path
import tempfile
from app.database import Database

with tempfile.TemporaryDirectory() as td:
    path=Path(td)/'test.db'

    db=Database(path)
    db.initialize()

    # İlk açılış: profil yok.
    assert db.has_profiles() is False
    assert db.profile_count()==0
    assert db.get_profile() is None
    assert db.active_profile_id() is None

    # İlk profil oluşturulunca kalıcı ve aktif olmalı.
    pid1=db.create_profile('Pelin Öğretmen','Öğretmen','A1',20)
    db.switch_profile(pid1)
    assert db.has_profiles() is True
    assert db.profile_count()==1
    assert db.get_profile()['name']=='Pelin Öğretmen'
    assert db.get_profile()['setup_complete']==1

    # Aynı DB ikinci kez açıldığında profil yeniden istenmemeli.
    reopened=Database(path)
    reopened.initialize()
    assert reopened.has_profiles() is True
    assert reopened.profile_count()==1
    assert reopened.get_profile()['name']=='Pelin Öğretmen'

    # Son kalan profil artık silinebilir.
    only_profile_id=reopened.active_profile_id()
    remains=reopened.delete_profile(only_profile_id)
    assert remains is False
    assert reopened.has_profiles() is False
    assert reopened.profile_count()==0
    assert reopened.active_profile_id() is None
    assert reopened.get_profile() is None

    # KRİTİK REGRESYON TESTİ:
    # Son profil silindikten sonra program kapatılıp yeniden açıldığında
    # legacy `profile` tablosundan profil tekrar oluşmamalı.
    after_delete_restart=Database(path)
    after_delete_restart.initialize()
    assert after_delete_restart.has_profiles() is False
    assert after_delete_restart.profile_count()==0
    assert after_delete_restart.active_profile_id() is None
    assert after_delete_restart.get_profile() is None

    # Son profil silindikten sonra yeniden profil oluşturulabilir.
    reopened=after_delete_restart
    pid1=reopened.create_profile('Pelin Öğretmen','Öğretmen','A1',20)
    reopened.switch_profile(pid1)
    assert reopened.has_profiles() is True
    assert reopened.profile_count()==1

    # 300 ders sistemi korunmalı.
    assert all(len(reopened.get_lessons(level))==50 for level in ('A1','A2','B1','B2','C1','C2'))
    assert sum(len(reopened.get_lessons(level)) for level in ('A1','A2','B1','B2','C1','C2'))==300

    first=reopened.next_lesson()
    assert first and first['position']==1
    reopened.complete_lesson(first['id'],100)
    assert reopened.current_level_progress()['completed']==1

    # Ek profil sistemi korunmalı.
    pid2=reopened.create_profile('Hacı Öğretmen','Öğretmen','B1',25)
    reopened.switch_profile(pid2)
    assert reopened.get_profile()['name']=='Hacı Öğretmen'
    assert reopened.get_profile()['current_level']=='B1'
    assert reopened.current_level_progress()['completed']==0

    reopened.switch_profile(pid1)
    assert reopened.current_level_progress()['completed']==1

    # İki profil varken aktif profil silinirse diğer profil otomatik aktif olur.
    reopened.switch_profile(pid2)
    remains=reopened.delete_profile(pid2)
    assert remains is True
    assert reopened.profile_count()==1
    assert reopened.active_profile_id()==pid1
    assert reopened.get_profile()['name']=='Pelin Öğretmen'

    # Sınıf sistemi korunmalı.
    cid=reopened.create_class('12/D','A1','2026-2027','Deneme sınıfı')
    lesson=reopened.get_lessons('A1')[0]
    plan=reopened.add_class_plan(cid,lesson['id'],'2026-09-15','Selamlaşma konusu')
    assert len(reopened.list_class_plans(cid))==1
    reopened.set_class_plan_status(plan,'İşlendi')
    assert reopened.list_class_plans(cid)[0]['status']=='İşlendi'

print('12/D Dil Programı v2.3 zorunlu profil self-test: PASS')
