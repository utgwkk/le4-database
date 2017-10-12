import os
import psycopg2
import psycopg2.extras
from hashlib import sha256
from dotenv import load_dotenv, find_dotenv
from flask import (
    Flask,
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


def passhash(password):
    return sha256(bytes(password + os.environ.get('PASSWORD_SALT', ''),
                        encoding='utf-8')).hexdigest()


def create_user(username, password, description):
    c = cursor()
    c.execute('INSERT INTO users (username, password, description) '
              'VALUES (%s, %s, %s)',
              (username, passhash(password), description))
    db().commit()


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
    c.execute('SELECT COUNT(*) AS cnt FROM users '
              'WHERE username = %s AND password = %s',
              (username, passhash(password)))
    return c.fetchone()['cnt'] > 0


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
    return {'logged_in': session['user_id'] is not None}


@app.context_processor
def current_user():
    c = cursor()
    c.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
    return {'current_user': c.fetchone()}


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()
        del g.db


@app.route('/')
def index():
    db()
    return '<H1>It works!</H1>'


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
        create_user(username, password, description)
        c = cursor()
        session['user_id'] = c.lastrowid
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
    if not session['user_id']:
        flash('You are not logged in')
        return redirect(url_for('login'))
    else:
        username = get_username_by_user_id(session['user_id'])
        return redirect(url_for('userpage', username=username))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
