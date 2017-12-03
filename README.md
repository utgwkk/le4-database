# Suxiv
計算機科学実験及演習4: データベース

## Requirements
* PostgreSQL 10.0
* Python 3.6
* pipenv

## Setup

```console
$ psql -d [dbname] < schema.sql
$ pipenv install
$ cp .env.example .env
$ vim .env
$ FLASK_APP=main.py pipenv run flask run
```
