from flask import Flask
app = Flask(__name__)
from flask import render_template, request, redirect, url_for, abort
import time
from hashids import Hashids
hashids = Hashids()

import sqlite3
from flask import g

DATABASE = 'urls.db'

def get_db():
  db = getattr(g, '_database', None)
  if db is None:
    db = g._database = sqlite3.connect(DATABASE)
  return db

@app.teardown_appcontext
def close_connection(exception):
  db = getattr(g, '_database', None)
  if db is not None:
    db.close()


@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')

@app.route('/', methods=['POST'])
def shorten_url():
  db = get_db()
  cursor = db.execute(
    'INSERT INTO urls (timestamp, original_url) VALUES (?, ?)',
    (int(time.time()), request.form['original_url'])
  )
  cursor.fetchall()
  db.commit()

  # generate hash with id
  url_hash = hashids.encode(cursor.lastrowid)

  url_tail = url_for('redirect_to_shortened_url', url_hash=url_hash)
  return 'http://' + request.host + url_tail

@app.route('/<url_hash>')
def redirect_to_shortened_url(url_hash=None):
  # decode hash to find id
  id = hashids.decode(url_hash)[0] # decode() returns tuple

  # if id doesn't exist, return 404 error
  if not get_db().execute('SELECT EXISTS(SELECT id FROM urls WHERE id=?)', (id,)).fetchall()[0][0]:
    abort(404)

  # else, redirect to original url
  original_url = get_db().execute(
    'SELECT original_url FROM urls WHERE id=?',
    (id,)
  ).fetchall()[0][0] # fetchall() returns tuple inside array
  return redirect(original_url)
