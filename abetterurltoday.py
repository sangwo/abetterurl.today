import os
from flask import Flask
from flask import render_template, request, redirect, url_for, abort, jsonify, g
import time
from hashids import Hashids
import sqlite3

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, 'urls.db')

NUM_SHORTENED_URLS_PER_DAY = 60

hashids = Hashids()
app = Flask(__name__)

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

  # limit shortening url to NUM_SHORTENED_URLS_PER_DAY times a day
  # TODO: limit it per computer(ip)
  today_year = int(time.strftime("%Y"))
  today_month = int(time.strftime("%m"))
  today_day = int(time.strftime("%d"))
  today = time.mktime(time.struct_time((today_year, today_month, today_day, 0, 0, 0, 0, 0, -1)))
  num_shortened_urls_today = db.execute(
    'SELECT count(*) FROM urls WHERE timestamp - ? >= 0',
    (today,)
  ).fetchall()[0][0]

  if num_shortened_urls_today >= NUM_SHORTENED_URLS_PER_DAY:
    # return error message
    error_message = "Sorry, you can shorten only {} times per day. Visit again tommorrow!".format(NUM_SHORTENED_URLS_PER_DAY) 
    return jsonify(error=True, error_message=error_message)
  else:
    # insert data into database and return shortened url
    cursor = db.execute(
      'INSERT INTO urls (timestamp, original_url) VALUES (?, ?)',
      (int(time.time()), request.form['original_url'])
    )
    cursor.fetchall()
    db.commit()

    # generate hash with id
    url_hash = hashids.encode(cursor.lastrowid)

    url_tail = url_for('redirect_to_shortened_url', url_hash=url_hash)
    shortened_url = 'http://' + request.host + url_tail
    return jsonify(error=False, shortened_url=shortened_url)

@app.route('/r/<url_hash>')
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
