import os
import psycopg2
from dotenv import load_dotenv, find_dotenv
from flask import Flask, g
load_dotenv(find_dotenv())
app = Flask(__name__)


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


@app.route('/')
def index():
    db()
    return '<H1>It works!</H1>'


if __name__ == '__main__':
    app.run()
