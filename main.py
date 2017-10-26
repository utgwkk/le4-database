import os
import random
import psycopg2
import psycopg2.extras
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
    return passhash(password, row['salt']) == row['password']


def get_user_id_by_username(username):
    c = cursor()
    c.execute('SELECT id FROM users WHERE username = %s', (username,))
    return c.fetchone()['id']


def get_username_by_user_id(user_id):
    c = cursor()
    c.execute('SELECT username FROM users WHERE id = %s', (user_id,))
    return c.fetchone()['username']


@app.context_processor
def logged_in():
    return {'logged_in': 'user_id' in session}


@app.context_processor
def current_user():
    c = cursor()
    c.execute('SELECT * FROM users WHERE id = %s', (session.get('user_id'),))
    return {'current_user': c.fetchone()}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if authenticate(username, password):
            session['user_id'] = get_user_id_by_username(username)
            flash('Login succeeded')
            return redirect(url_for('mypage'))
        else:
            flash('Login failed')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You are not logged in')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        description = request.args.get('description', '')
        try:
            validate_user_params(username, password)
        except ValidationError as e:
            flash(e.message)
            return redirect(url_for('register_user'))
        alphabets = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        salt = ''.join([random.choice(alphabets) for _ in range(32)])
        with db() as conn:
            c = conn.cursor()
            c.execute(
                'INSERT INTO users (username, salt, password, description) '
                'VALUES (%s, %s, %s, %s) RETURNING id',
                (username, salt, passhash(password, salt), description)
            )
        lastrowid = c.fetchone()[0]
        session['user_id'] = lastrowid
        flash('Registration succeeded')
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


@app.route('/mypage')
def mypage():
    if not logged_in()['logged_in']:
        flash('You are not logged in')
        return redirect(url_for('login'))
    else:
        username = get_username_by_user_id(session['user_id'])
        return redirect(url_for('userpage', username=username))


@app.route('/setting', methods=['GET', 'POST'])
def setting():
    if request.method == 'POST':
        if not logged_in()['logged_in']:
            flash('You are not logged in')
            return redirect(url_for('login'))
        description = request.form['description']
        with db() as conn:
            c = conn.cursor()
            c.execute('UPDATE users SET description = %s '
                      'WHERE id = %s',
                      (description, session['user_id'],))
        flash('Settings changed')
        return redirect(url_for('setting'))
    else:
        if not logged_in()['logged_in']:
            flash('You are not logged in')
            return redirect(url_for('login'))
        user = current_user()['current_user']
        return render_template('setting.html', user=user)


@app.route('/initialize')
def initialize():
    with db() as conn:
        c = conn.cursor()
        c.execute('TRUNCATE users')
        c.execute("SELECT SETVAL ('users_id_seq', 1, false)")
    return Response('ok', mimetype='text/plain')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
