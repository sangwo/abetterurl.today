from flask import Flask
app = Flask(__name__)
from flask import render_template, request, redirect, url_for
import time

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

  url_tail = url_for('redirect_to_shortened_url', id=cursor.lastrowid)
  return 'http://' + request.host + url_tail

@app.route('/<id>')
def redirect_to_shortened_url(id=None):
  original_url = get_db().execute(
    'SELECT original_url FROM urls WHERE id=?',
    (id,)
  ).fetchall()[0][0] # fetchall() >> tuple inside array
  return redirect(original_url)
