import os
import random
import glob
import psycopg2
import psycopg2.extras
import psycopg2.errorcodes
from functools import wraps
from hashlib import sha256
from dotenv import load_dotenv, find_dotenv
from flask import (
    Flask,
    Response,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
load_dotenv(find_dotenv())
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER')


def connect_db():
    if hasattr(app, 'testing') and app.testing:
        return psycopg2.connect(
            host=os.environ.get('POSTGRESQL_HOST', 'localhost'),
            port=os.environ.get('POSTGRESQL_PORT', 5432),
            user=os.environ.get('POSTGRESQL_USER'),
            password=os.environ.get('POSTGRESQL_PASS'),
            dbname=os.environ.get('TEST_POSTGRESQL_DB'),
        )
    else:
        return psycopg2.connect(
            host=os.environ.get('POSTGRESQL_HOST', 'localhost'),
            port=os.environ.get('POSTGRESQL_PORT', 5432),
            user=os.environ.get('POSTGRESQL_USER'),
            password=os.environ.get('POSTGRESQL_PASS'),
            dbname=os.environ.get('POSTGRESQL_DB'),
        )


def db():
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db


def cursor():
    return db().cursor(cursor_factory=psycopg2.extras.DictCursor)


def passhash(password, salt):
    return sha256(bytes(password + salt, encoding='utf-8')).hexdigest()


class ValidationError(Exception):
    def __init__(self, message):
        self.message = message


def validate_user_params(username, password):
    if len(username) < 4:
        raise ValidationError('username should be at least 4 characters')
    if len(username) > 64:
        raise ValidationError('username should be shorter than 32 characters')
    if len(password) < 6:
        raise ValidationError('password should be at least 6 characters')


def authenticate(username, password):
    c = cursor()
    c.execute('SELECT password, salt FROM users WHERE username = %s',
              (username,))
    row = c.fetchone()
    return row and passhash(password, row['salt']) == row['password']


def get_user_id_by_username(username):
    c = cursor()
    c.execute('SELECT id FROM users WHERE username = %s', (username,))
    return c.fetchone()['id']


def get_username_by_user_id(user_id):
    c = cursor()
    c.execute('SELECT username FROM users WHERE id = %s', (user_id,))
    return c.fetchone()['username']


def ext2mime(ext):
    return {
        '.gif': 'image/gif',
        '.jpg': 'image/jpeg',
        '.png': 'image/png',
    }.get(ext)


@app.context_processor
def logged_in():
    return {'logged_in': 'user_id' in session}


@app.context_processor
def current_user():
    c = cursor()
    c.execute('SELECT * FROM users WHERE id = %s', (session.get('user_id'),))
    return {'current_user': c.fetchone()}


@app.context_processor
def follows():
    def _follows(follower_id, following_id):
        c = cursor()
        c.execute('SELECT 1 FROM relations '
                  'WHERE follower_id = %s AND following_id = %s',
                  (follower_id, following_id))
        return c.fetchone() is not None
    return {'follows': _follows}


@app.context_processor
def favorites():
    def _favorites(user_id, post_id):
        c = cursor()
        c.execute('SELECT 1 FROM favorites '
                  'WHERE user_id = %s AND post_id = %s',
                  (user_id, post_id))
        return c.fetchone() is not None
    return {'favorites': _favorites}


def must_login(f):
    @wraps(f)
    def _inner(*args, **kwargs):
        if not logged_in()['logged_in']:
            flash('You are not logged in', 'info')
            return redirect(url_for('login'))
        else:
            return f(*args, **kwargs)
    return _inner


@app.route('/')
def index():
    c = cursor()
    c.execute('''
        SELECT p.id, p.title, p.description, u.username
        FROM posts p
        LEFT JOIN users u
        ON p.user_id = u.id
        ORDER BY p.id DESC LIMIT 8
    ''')
    posts = c.fetchall()
    if logged_in()['logged_in']:
        c.execute('''
            SELECT p.id, p.title, p.description, u.username
            FROM posts p
            LEFT JOIN users u
            ON p.user_id = u.id
            WHERE p.user_id IN (
                SELECT following_id FROM relations
                WHERE follower_id = %s
            )
            ORDER BY p.id DESC LIMIT 8
        ''', (session['user_id'],))
        posts_following = c.fetchall()
    else:
        posts_following = []
    return render_template('index.html', posts=posts, posts_following=posts_following)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if authenticate(username, password):
            session['user_id'] = get_user_id_by_username(username)
            flash('Login succeeded', 'info')
            if 'back_url' in session:
                url = session['back_url']
                session.pop('back_url', None)
                return redirect(url)
            else:
                return redirect(url_for('mypage'))
        else:
            flash('Login failed', 'error')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You are not logged in', 'info')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        description = request.form.get('description', '')
        try:
            validate_user_params(username, password)
        except ValidationError as e:
            flash(e.message, 'error')
            return redirect(url_for('register_user'))
        alphabets = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        salt = ''.join([random.choice(alphabets) for _ in range(32)])
        with db() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    'INSERT INTO users (username, salt, password, description) '
                    'VALUES (%s, %s, %s, %s) RETURNING id',
                    (username, salt, passhash(password, salt), description)
                )
            except psycopg2.Error as e:
                if e.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                    flash(f'The username @{username} has already taken', 'error')
                else:
                    flash(f'Unknown error: {e.pgerror}', 'error')
                return redirect(url_for('register_user'))
        lastrowid = c.fetchone()[0]
        session['user_id'] = lastrowid
        flash('Registration succeeded', 'info')
        return redirect(url_for('mypage'))
    else:
        return render_template('register.html')


@app.route('/@<string:username>')
def userpage(username):
    c = cursor()
    c.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = c.fetchone()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


@app.route('/following')
@must_login
def following():
    c = cursor()
    c.execute('SELECT u.* FROM relations r '
              'INNER JOIN users u '
              'ON u.id = r.following_id AND r.follower_id = %s '
              'ORDER BY created_at DESC',
              (session['user_id'],))
    return render_template('following.html', users=c.fetchall())


@app.route('/follower')
@must_login
def follower():
    c = cursor()
    c.execute('SELECT u.* FROM relations r '
              'INNER JOIN users u '
              'ON u.id = r.follower_id AND r.following_id = %s '
              'ORDER BY created_at DESC',
              (session['user_id'],))
    return render_template('follower.html', users=c.fetchall())


@app.route('/follow', methods=['POST'])
@must_login
def follow():
    if request.method != 'POST':
        abort(400)
    username = request.form.get('username', '')
    user_id = get_user_id_by_username(username)
    with db() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO relations (follower_id, following_id) '
                  'VALUES (%s, %s)', (session['user_id'], user_id))
    flash('Follow successful', 'info')
    return redirect(url_for('userpage', username=username))


@app.route('/unfollow', methods=['POST'])
@must_login
def unfollow():
    if request.method != 'POST':
        abort(400)
    username = request.form.get('username', '')
    user_id = get_user_id_by_username(username)
    c = db().cursor()
    c.execute('DELETE FROM relations '
              'WHERE follower_id = %s AND following_id = %s',
              (session['user_id'], user_id))
    db().commit()
    flash('Unfollow successful', 'info')
    return redirect(url_for('userpage', username=username))


@app.route('/mypage')
@must_login
def mypage():
    username = get_username_by_user_id(session['user_id'])
    return redirect(url_for('userpage', username=username))


@app.route('/setting', methods=['GET', 'POST'])
@must_login
def setting():
    if request.method == 'POST':
        description = request.form['description']
        with db() as conn:
            c = conn.cursor()
            c.execute('UPDATE users SET description = %s, updated_at = NOW() '
                      'WHERE id = %s',
                      (description, session['user_id'],))
        flash('Settings changed', 'info')
        return redirect(url_for('setting'))
    else:
        user = current_user()['current_user']
        return render_template('setting.html', user=user)


@app.route('/upload', methods=['GET', 'POST'])
@must_login
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file specified', 'error')
            return redirect(url_for('upload'))

        title = request.form['title']
        description = request.form['description']
        upload_file = request.files['file']
        _, ext = os.path.splitext(upload_file.filename)
        filedata = upload_file.read()
        filename = sha256(filedata).hexdigest() + ext
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with db() as conn:
            c = conn.cursor()
            c.execute('INSERT INTO posts (user_id, title, description, path) '
                      'VALUES (%s, %s, %s, %s) RETURNING id',
                      (session['user_id'], title, description, filename))
            new_post_id = c.fetchone()[0]
            with open(filepath, 'wb') as f:
                f.write(filedata)
        return redirect(url_for('show_post', id=new_post_id))
    else:
        return render_template('upload.html')


@app.route('/post/<int:id>')
def show_post(id):
    c = cursor()
    c.execute('''
        SELECT p.id, p.title, p.description, p.path, p.user_id
        FROM posts p
        WHERE id = %s
    ''', (id,))
    data = dict(c.fetchone())
    c.execute('SELECT COUNT(*) AS cnt FROM favorites WHERE post_id = %s', (id,))
    data['favorites_count'] = c.fetchone()['cnt']
    return render_template('post.html', **data)


@app.route('/post/<int:id>/image')
def image(id):
    c = cursor()
    c.execute('''
        SELECT path FROM posts
        WHERE id = %s
    ''', (id,))
    path = c.fetchone()['path']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], path)
    with open(filepath, 'rb') as f:
        data = f.read()
        return Response(data, mimetype=ext2mime(os.path.splitext(path)[1]))


@app.route('/favorites')
@must_login
def list_favorite():
    c = cursor()
    c.execute('''
    SELECT p.id, p.title, p.description, u.username
    FROM favorites f
    INNER JOIN posts p
    ON f.user_id = %s
    AND f.post_id = p.id
    INNER JOIN users u
    ON p.user_id = u.id
    ORDER BY f.created_at DESC
    ''', (session['user_id'],))
    posts = c.fetchall()
    return render_template('favorites.html', posts=posts)


@app.route('/favorite/<int:post_id>', methods=['POST'])
@must_login
def create_favorite(post_id):
    c = cursor()
    c.execute('''
    INSERT INTO favorites (user_id, post_id)
    VALUES (%s, %s)
    ''', (session['user_id'], post_id,))
    db().commit()
    return redirect(url_for('show_post', id=post_id))


@app.route('/unfavorite/<int:post_id>', methods=['POST'])
@must_login
def delete_favorite(post_id):
    c = cursor()
    c.execute('''
    DELETE FROM favorites
    WHERE user_id = %s AND post_id = %s
    ''', (session['user_id'], post_id,))
    db().commit()
    return redirect(url_for('show_post', id=post_id))


@app.route('/initialize')
def initialize():
    with db() as conn:
        c = conn.cursor()
        c.execute('TRUNCATE relations')
        c.execute('TRUNCATE users CASCADE')
        c.execute("SELECT SETVAL ('users_id_seq', 1, false)")
        c.execute('TRUNCATE posts CASCADE')
        c.execute("SELECT SETVAL ('posts_id_seq', 1, false)")
        c.execute('TRUNCATE favorites CASCADE')
    for path in glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*')):
        os.remove(path)
    return Response('ok', mimetype='text/plain')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
