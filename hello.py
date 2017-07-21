from flask import Flask
app = Flask(__name__)
from flask import render_template, request

@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')

@app.route('/', methods=['POST'])
def shorten_url():
  return request.form['original_url']
