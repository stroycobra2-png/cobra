import argparse
import json
import os
import secrets
import socket
from datetime import date, datetime, timedelta
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, send_from_directory, session, url_for
from waitress import serve

from app.database import Database, LEVEL_ORDER

BASE_DIR = Path(__file__).resolve().parent
MOBILE_DIR = BASE_DIR / 'mobile_web'
STATIC_DIR = MOBILE_DIR / 'static'
TEMPLATE_DIR = MOBILE_DIR / 'templates'

DB = Database()
DB.initialize()

MOBILE_PIN = os.environ.get('DIL_MOBILE_PIN') or f"{secrets.randbelow(1000000):06d}"
PORT = int(os.environ.get('DIL_MOBILE_PORT', '5050'))

app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR), static_url_path='/static')
app.secret_key = os.environ.get('DIL_MOBILE_SECRET') or secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(days=30),
)


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        return s.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return '127.0.0.1'
    finally:
        s.close()


def get_profile(pid):
    if not pid:
        return None
    with DB.connect() as c:
        return c.execute('SELECT * FROM profiles WHERE id=?', (pid,)).fetchone()


def all_profiles():
    with DB.connect() as c:
        return c.execute('SELECT * FROM profiles ORDER BY name COLLATE NOCASE').fetchall()


def mobile_profile_id():
    pid = session.get('mobile_profile_id')
    if get_profile(pid):
        return int(pid)
    profiles = all_profiles()
    if not profiles:
        session.pop('mobile_profile_id', None)
        return None
    session['mobile_profile_id'] = profiles[0]['id']
    return int(profiles[0]['id'])


def current_profile():
    return get_profile(mobile_profile_id())


def accessible_level(pid, code):
    p = get_profile(pid)
    return bool(p and code in LEVEL_ORDER and LEVEL_ORDER.index(code) <= LEVEL_ORDER.index(p['current_level']))


def lessons_for(pid, level):
    with DB.connect() as c:
        return c.execute(
            '''SELECT l.*,COALESCE(p.completed,0) completed,
               COALESCE(p.best_score,0) best_score,COALESCE(p.attempts,0) attempts
               FROM lessons l LEFT JOIN lesson_progress_v2 p
               ON p.lesson_id=l.id AND p.profile_id=?
               WHERE l.level_code=? ORDER BY l.position''',
            (pid, level),
        ).fetchall()


def lesson_for(pid, lesson_id):
    with DB.connect() as c:
        return c.execute(
            '''SELECT l.*,COALESCE(p.completed,0) completed,
               COALESCE(p.best_score,0) best_score,COALESCE(p.attempts,0) attempts
               FROM lessons l LEFT JOIN lesson_progress_v2 p
               ON p.lesson_id=l.id AND p.profile_id=? WHERE l.id=?''',
            (pid, lesson_id),
        ).fetchone()


def lesson_accessible(pid, lesson_id):
    lesson = lesson_for(pid, lesson_id)
    if not lesson or not accessible_level(pid, lesson['level_code']):
        return False
    if lesson['position'] == 1:
        return True
    with DB.connect() as c:
        prev = c.execute(
            '''SELECT COALESCE(p.completed,0) completed
               FROM lessons l LEFT JOIN lesson_progress_v2 p
               ON p.lesson_id=l.id AND p.profile_id=?
               WHERE l.level_code=? AND l.position=?''',
            (pid, lesson['level_code'], lesson['position'] - 1),
        ).fetchone()
    return bool(prev and prev['completed'])


def touch_streak(c, pid):
    p = c.execute('SELECT streak,last_study_date FROM profiles WHERE id=?', (pid,)).fetchone()
    if not p:
        return
    today = date.today()
    last = date.fromisoformat(p['last_study_date']) if p['last_study_date'] else None
    if last == today:
        return
    streak = p['streak'] + 1 if last == today - timedelta(days=1) else 1
    c.execute('UPDATE profiles SET streak=?,last_study_date=? WHERE id=?', (streak, today.isoformat(), pid))


def unlock_achievements(c, pid):
    completed = c.execute(
        'SELECT COUNT(*) n FROM lesson_progress_v2 WHERE profile_id=? AND completed=1', (pid,)
    ).fetchone()['n']
    reviews = c.execute(
        "SELECT COUNT(*) n FROM study_log_v2 WHERE profile_id=? AND activity='Kelime tekrarı'", (pid,)
    ).fetchone()['n']
    p = c.execute('SELECT xp,streak FROM profiles WHERE id=?', (pid,)).fetchone()
    unlock = []
    if completed >= 1:
        unlock.append('first_lesson')
    if completed >= 10:
        unlock.append('ten_lessons')
    if p['xp'] >= 100:
        unlock.append('xp_100')
    if p['xp'] >= 500:
        unlock.append('xp_500')
    if p['streak'] >= 3:
        unlock.append('streak_3')
    if p['streak'] >= 7:
        unlock.append('streak_7')
    if reviews >= 1:
        unlock.append('first_review')
    now = datetime.now().isoformat(timespec='seconds')
    for code in unlock:
        c.execute(
            'UPDATE profile_achievements SET unlocked=1,unlocked_at=COALESCE(unlocked_at,?) WHERE profile_id=? AND code=?',
            (now, pid, code),
        )


def complete_lesson_for(pid, lesson_id, score):
    lesson = lesson_for(pid, lesson_id)
    if not lesson or not lesson_accessible(pid, lesson_id):
        return 0
    first = not bool(lesson['completed'])
    earned = 30 if first else 8
    now = datetime.now().isoformat(timespec='seconds')
    with DB.connect() as c:
        c.execute(
            '''INSERT INTO lesson_progress_v2(profile_id,lesson_id,completed,best_score,attempts,completed_at)
               VALUES(?,?,1,?,1,?) ON CONFLICT(profile_id,lesson_id) DO UPDATE SET
               completed=1,best_score=MAX(best_score,excluded.best_score),
               attempts=attempts+1,completed_at=excluded.completed_at''',
            (pid, lesson_id, score, now),
        )
        for v in json.loads(lesson['vocabulary']):
            c.execute(
                '''INSERT OR IGNORE INTO vocabulary_progress_v2(
                   profile_id,level_code,word,translation,example,due_date)
                   VALUES(?,?,?,?,?,?)''',
                (
                    pid,
                    lesson['level_code'],
                    v['word'],
                    v['translation'],
                    v.get('example', ''),
                    date.today().isoformat(),
                ),
            )
        touch_streak(c, pid)
        c.execute('UPDATE profiles SET xp=xp+? WHERE id=?', (earned, pid))
        c.execute(
            '''INSERT INTO study_log_v2(profile_id,activity,skill,score,xp,minutes,created_at)
               VALUES(?,?,?,?,?,?,?)''',
            (pid, f"Ders: {lesson['title']}", 'grammar', score, earned, 8, now),
        )

        total = c.execute('SELECT COUNT(*) n FROM lessons WHERE level_code=?', (lesson['level_code'],)).fetchone()['n']
        done = c.execute(
            '''SELECT COUNT(*) n FROM lesson_progress_v2 p JOIN lessons l ON l.id=p.lesson_id
               WHERE p.profile_id=? AND p.completed=1 AND l.level_code=?''',
            (pid, lesson['level_code']),
        ).fetchone()['n']
        if total and done >= total:
            idx = LEVEL_ORDER.index(lesson['level_code'])
            p = c.execute('SELECT current_level FROM profiles WHERE id=?', (pid,)).fetchone()
            if p and p['current_level'] == lesson['level_code'] and idx < len(LEVEL_ORDER) - 1:
                c.execute('UPDATE profiles SET current_level=? WHERE id=?', (LEVEL_ORDER[idx + 1], pid))
        unlock_achievements(c, pid)
        c.commit()
    return earned


def review_word_for(pid, word_id, quality):
    with DB.connect() as c:
        row = c.execute(
            'SELECT * FROM vocabulary_progress_v2 WHERE id=? AND profile_id=?', (word_id, pid)
        ).fetchone()
        if not row:
            return False
        reps, ease, interval = row['repetitions'], row['ease'], row['interval_days']
        if quality == 'hard':
            reps, interval, ease = 0, 1, max(1.3, ease - 0.2)
        elif quality == 'medium':
            reps += 1
            interval = 1 if reps == 1 else max(2, int(max(1, interval) * ease * 0.7))
        else:
            reps += 1
            interval = 1 if reps == 1 else 3 if reps == 2 else max(4, int(max(1, interval) * ease))
            ease = min(3.0, ease + 0.1)
        due = date.today() + timedelta(days=interval)
        c.execute(
            '''UPDATE vocabulary_progress_v2 SET repetitions=?,interval_days=?,ease=?,due_date=?,last_result=?
               WHERE id=? AND profile_id=?''',
            (reps, interval, ease, due.isoformat(), quality, word_id, pid),
        )
        touch_streak(c, pid)
        c.execute('UPDATE profiles SET xp=xp+5 WHERE id=?', (pid,))
        c.execute(
            '''INSERT INTO study_log_v2(profile_id,activity,skill,score,xp,minutes,created_at)
               VALUES(?,?,?,?,?,?,?)''',
            (
                pid,
                'Kelime tekrarı',
                'vocabulary',
                100 if quality == 'easy' else 70 if quality == 'medium' else 40,
                5,
                1,
                datetime.now().isoformat(timespec='seconds'),
            ),
        )
        unlock_achievements(c, pid)
        c.commit()
    return True


def dashboard_data(pid):
    p = get_profile(pid)
    today_prefix = date.today().isoformat() + '%'
    with DB.connect() as c:
        total = c.execute('SELECT COUNT(*) n FROM lessons').fetchone()['n']
        completed = c.execute(
            'SELECT COUNT(*) n FROM lesson_progress_v2 WHERE profile_id=? AND completed=1', (pid,)
        ).fetchone()['n']
        words = c.execute('SELECT COUNT(*) n FROM vocabulary_progress_v2 WHERE profile_id=?', (pid,)).fetchone()['n']
        due = c.execute(
            'SELECT COUNT(*) n FROM vocabulary_progress_v2 WHERE profile_id=? AND due_date<=?',
            (pid, date.today().isoformat()),
        ).fetchone()['n']
        minutes = c.execute(
            'SELECT COALESCE(SUM(minutes),0) n FROM study_log_v2 WHERE profile_id=?', (pid,)
        ).fetchone()['n']
        today = c.execute(
            '''SELECT COUNT(*) activities,COALESCE(SUM(xp),0) xp,COALESCE(SUM(minutes),0) minutes
               FROM study_log_v2 WHERE profile_id=? AND created_at LIKE ?''',
            (pid, today_prefix),
        ).fetchone()
        recent = c.execute(
            'SELECT * FROM study_log_v2 WHERE profile_id=? ORDER BY id DESC LIMIT 5', (pid,)
        ).fetchall()
        classes = c.execute(
            '''SELECT c.*,
               (SELECT COUNT(*) FROM class_lesson_plans cp WHERE cp.class_id=c.id) plan_count,
               (SELECT COUNT(*) FROM class_lesson_plans cp WHERE cp.class_id=c.id AND cp.status='İşlendi') done_count
               FROM classes c WHERE owner_profile_id=? ORDER BY c.name''',
            (pid,),
        ).fetchall()

    level_lessons = lessons_for(pid, p['current_level'])
    level_done = sum(1 for x in level_lessons if x['completed'])
    nxt = next((x for x in level_lessons if not x['completed'] and lesson_accessible(pid, x['id'])), None)
    return {
        'profile': p,
        'total': total,
        'completed': completed,
        'words': words,
        'due': due,
        'minutes': minutes,
        'today': today,
        'recent': recent,
        'classes': classes,
        'level_done': level_done,
        'level_total': len(level_lessons),
        'level_percent': round(level_done / max(1, len(level_lessons)) * 100),
        'next': nxt,
    }


def set_mobile_profile(pid):
    if not get_profile(pid):
        return False
    session['mobile_profile_id'] = int(pid)
    return True


@app.before_request
def access_gate():
    endpoint = request.endpoint or ''
    public = {'pair', 'static', 'manifest', 'service_worker', 'offline'}
    if endpoint in public:
        return None
    if not session.get('paired'):
        return redirect(url_for('pair'))
    if not DB.has_profiles() and endpoint != 'create_profile':
        return redirect(url_for('create_profile'))
    mobile_profile_id()
    return None


@app.context_processor
def inject_globals():
    return {
        'active_profile': current_profile() if session.get('paired') and DB.has_profiles() else None,
        'all_profiles_nav': all_profiles() if session.get('paired') and DB.has_profiles() else [],
    }


@app.route('/pair', methods=['GET', 'POST'])
def pair():
    if request.method == 'POST':
        entered = ''.join(ch for ch in request.form.get('pin', '') if ch.isdigit())
        if secrets.compare_digest(entered, MOBILE_PIN):
            session.clear()
            session.permanent = True
            session['paired'] = True
            profiles = all_profiles()
            if profiles:
                session['mobile_profile_id'] = profiles[0]['id']
            return redirect(url_for('dashboard') if profiles else url_for('create_profile'))
        flash('Bağlantı kodu yanlış.', 'error')
    return render_template('pair.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('pair'))


@app.route('/profile/create', methods=['GET', 'POST'])
def create_profile():
    if not session.get('paired'):
        return redirect(url_for('pair'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        role = request.form.get('role', 'Öğretmen')
        level = request.form.get('level', 'A1')
        try:
            goal = max(5, min(180, int(request.form.get('goal', '20'))))
        except ValueError:
            goal = 20
        if not name:
            flash('Profil adı boş olamaz.', 'error')
        else:
            pid = DB.create_profile(name, role, level, goal)
            set_mobile_profile(pid)
            flash('Profil oluşturuldu.', 'success')
            return redirect(url_for('dashboard'))
    return render_template('create_profile.html', levels=LEVEL_ORDER)


@app.route('/')
def dashboard():
    pid = mobile_profile_id()
    if not pid:
        return redirect(url_for('create_profile'))
    return render_template('dashboard.html', d=dashboard_data(pid))


@app.route('/profiles')
def profiles():
    return render_template('profiles.html', profiles=all_profiles(), active_id=mobile_profile_id())


@app.post('/profile/switch/<int:pid>')
def switch_profile(pid):
    if not set_mobile_profile(pid):
        abort(404)
    flash('Mobil profil değiştirildi.', 'success')
    return redirect(request.referrer or url_for('dashboard'))


@app.route('/lessons')
def lessons():
    pid = mobile_profile_id()
    p = get_profile(pid)
    level = request.args.get('level') or p['current_level']
    if level not in LEVEL_ORDER:
        level = p['current_level']
    if not accessible_level(pid, level):
        level = p['current_level']
    rows = lessons_for(pid, level)
    decorated = []
    for r in rows:
        d = dict(r)
        d['accessible'] = lesson_accessible(pid, r['id'])
        decorated.append(d)
    return render_template('lessons.html', lessons=decorated, selected_level=level, levels=LEVEL_ORDER, profile=p)


@app.route('/lesson/<int:lesson_id>', methods=['GET', 'POST'])
def lesson(lesson_id):
    pid = mobile_profile_id()
    l = lesson_for(pid, lesson_id)
    if not l:
        abort(404)
    if not lesson_accessible(pid, lesson_id):
        flash('Bu ders kilitli. Önce önceki dersi tamamla.', 'error')
        return redirect(url_for('lessons', level=l['level_code']))
    quiz = json.loads(l['quiz'])
    vocab = json.loads(l['vocabulary'])
    if request.method == 'POST':
        answers = []
        for i in range(len(quiz)):
            try:
                answers.append(int(request.form.get(f'q{i}', '-1')))
            except ValueError:
                answers.append(-1)
        if any(x < 0 for x in answers):
            flash('Tüm soruları cevapla.', 'error')
        else:
            correct = sum(1 for ans, q in zip(answers, quiz) if ans == q['correct'])
            score = round(correct / max(1, len(quiz)) * 100)
            if score >= 67:
                xp = complete_lesson_for(pid, lesson_id, score)
                flash(f'Ders tamamlandı • %{score} • +{xp} XP', 'success')
                return redirect(url_for('lessons', level=l['level_code']))
            with DB.connect() as c:
                touch_streak(c, pid)
                c.execute('UPDATE profiles SET xp=xp+3 WHERE id=?', (pid,))
                c.execute(
                    '''INSERT INTO study_log_v2(profile_id,activity,skill,score,xp,minutes,created_at)
                       VALUES(?,?,?,?,?,?,?)''',
                    (pid, 'Quiz denemesi', 'grammar', score, 3, 3, datetime.now().isoformat(timespec='seconds')),
                )
                c.commit()
            flash(f'Skor %{score}. Dersi tamamlamak için en az %67 gerekiyor.', 'error')
    return render_template('lesson.html', lesson=l, quiz=quiz, vocab=vocab)


@app.route('/words')
def words():
    pid = mobile_profile_id()
    q = request.args.get('q', '').strip().lower()
    fav = request.args.get('fav') == '1'
    with DB.connect() as c:
        rows = c.execute(
            'SELECT * FROM vocabulary_progress_v2 WHERE profile_id=? ORDER BY level_code,word', (pid,)
        ).fetchall()
        due = c.execute(
            'SELECT COUNT(*) n FROM vocabulary_progress_v2 WHERE profile_id=? AND due_date<=?',
            (pid, date.today().isoformat()),
        ).fetchone()['n']
    filtered = []
    for r in rows:
        if q and q not in r['word'].lower() and q not in r['translation'].lower():
            continue
        if fav and not r['favorite']:
            continue
        filtered.append(r)
    return render_template('words.html', words=filtered, total=len(rows), due=due, q=q, fav=fav)


@app.post('/word/<int:word_id>/favorite')
def favorite(word_id):
    pid = mobile_profile_id()
    with DB.connect() as c:
        c.execute(
            '''UPDATE vocabulary_progress_v2 SET favorite=CASE favorite WHEN 1 THEN 0 ELSE 1 END
               WHERE id=? AND profile_id=?''',
            (word_id, pid),
        )
        c.commit()
    return redirect(request.referrer or url_for('words'))


@app.route('/review', methods=['GET', 'POST'])
def review():
    pid = mobile_profile_id()
    if request.method == 'POST':
        try:
            word_id = int(request.form.get('word_id', '0'))
        except ValueError:
            word_id = 0
        quality = request.form.get('quality')
        if quality in ('hard', 'medium', 'easy'):
            review_word_for(pid, word_id, quality)
            return redirect(url_for('review'))
    with DB.connect() as c:
        word = c.execute(
            '''SELECT * FROM vocabulary_progress_v2 WHERE profile_id=? AND due_date<=?
               ORDER BY due_date,id LIMIT 1''',
            (pid, date.today().isoformat()),
        ).fetchone()
        count = c.execute(
            'SELECT COUNT(*) n FROM vocabulary_progress_v2 WHERE profile_id=? AND due_date<=?',
            (pid, date.today().isoformat()),
        ).fetchone()['n']
    return render_template('review.html', word=word, count=count)


@app.route('/classes')
def classes():
    pid = mobile_profile_id()
    with DB.connect() as c:
        rows = c.execute(
            '''SELECT c.*,
               (SELECT COUNT(*) FROM class_lesson_plans p WHERE p.class_id=c.id) plan_count,
               (SELECT COUNT(*) FROM class_lesson_plans p WHERE p.class_id=c.id AND p.status='İşlendi') done_count
               FROM classes c WHERE c.owner_profile_id=? ORDER BY c.name COLLATE NOCASE''',
            (pid,),
        ).fetchall()
    return render_template('classes.html', classes=rows)


@app.route('/class/<int:class_id>')
def class_detail(class_id):
    pid = mobile_profile_id()
    with DB.connect() as c:
        cls = c.execute('SELECT * FROM classes WHERE id=? AND owner_profile_id=?', (class_id, pid)).fetchone()
        if not cls:
            abort(404)
        plans = c.execute(
            '''SELECT p.*,l.level_code,l.unit,l.position,l.title lesson_title
               FROM class_lesson_plans p JOIN lessons l ON l.id=p.lesson_id
               WHERE p.class_id=? ORDER BY CASE WHEN p.planned_date='' THEN 1 ELSE 0 END,p.planned_date,p.id''',
            (class_id,),
        ).fetchall()
    return render_template('class_detail.html', cls=cls, plans=plans)


@app.post('/class-plan/<int:plan_id>/toggle')
def toggle_class_plan(plan_id):
    pid = mobile_profile_id()
    with DB.connect() as c:
        row = c.execute(
            '''SELECT p.status FROM class_lesson_plans p JOIN classes c ON c.id=p.class_id
               WHERE p.id=? AND c.owner_profile_id=?''',
            (plan_id, pid),
        ).fetchone()
        if not row:
            abort(404)
        new = 'Bekliyor' if row['status'] == 'İşlendi' else 'İşlendi'
        c.execute('UPDATE class_lesson_plans SET status=? WHERE id=?', (new, plan_id))
        c.commit()
    return redirect(request.referrer or url_for('classes'))


@app.route('/offline')
def offline():
    return render_template('offline.html')


@app.route('/manifest.webmanifest')
def manifest():
    return send_from_directory(STATIC_DIR, 'manifest.webmanifest', mimetype='application/manifest+json')


@app.route('/sw.js')
def service_worker():
    return send_from_directory(STATIC_DIR, 'sw.js', mimetype='application/javascript')


def main():
    parser = argparse.ArgumentParser(description='12/D Dil Programı mobil sunucusu')
    parser.add_argument('--host', default=os.environ.get('DIL_MOBILE_HOST', '0.0.0.0'))
    parser.add_argument('--port', type=int, default=PORT)
    args = parser.parse_args()
    ip = local_ip()
    print('')
    print('=' * 58)
    print('  12/D DIL PROGRAMI - TELEFON MODU')
    print('=' * 58)
    print(f'  Telefon adresi : http://{ip}:{args.port}')
    print(f'  Baglanti kodu  : {MOBILE_PIN}')
    print('  Telefon ve bilgisayar ayni Wi-Fi aginda olmali.')
    print('  Bu pencere acik kaldigi surece telefon modu calisir.')
    print('=' * 58)
    print('')
    serve(app, host=args.host, port=args.port, threads=6)


if __name__ == '__main__':
    main()
