#Adapted from the "flaskr" tutorial at http://flask.pocoo.org/

import sqlite3
import os, time, datetime
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from contextlib import closing
import pickle

# configuration
DATABASE = '/var/www/web-print-server/web-print-server/db/data.db'
DEBUG = True
SECRET_KEY = 'keepitsecretkeepitsafe'
USERNAME = 'devx'
PASSWORD = 'devx'


app = Flask(__name__)
app.config.from_object(__name__)

#database helper functions
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('db/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

#request helper functions
@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

#other helpers
def format_time(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S - %m/%d/%Y')

#default view
@app.route('/')
def show_entries():
    cur = g.db.execute('SELECT time, printer, copies, success FROM Entries ORDER BY id DESC')
    entries = [dict(time=format_time(row[0]), printer=row[1], copies=row[2], success=row[3]) for row in cur.fetchall()]
    numreq = g.db.execute('SELECT COUNT(*) FROM Entries').fetchone()[0]
    dayreq = g.db.execute('SELECT COUNT(*) FROM Entries WHERE time > ?', [time.time()-86400]).fetchone()[0]
    return render_template('layout.html', entries=entries, numrequests=numreq, dayrequests=dayreq)

@app.route('/add', methods=['POST'])
def add_entry():
    g.db.execute('INSERT INTO entries (time, printer, copies, success) VALUES (?, ?, ?, ?)',
                 [time.time(), request.form['printer'], request.form['copies'], request.form['success']])
    g.db.commit()
    return redirect(url_for('show_entries'))

@app.route('/hide', methods=['POST'])
def hide_successful():
    cur = g.db.execute('SELECT time, printer, copies, success FROM Entries WHERE success == 0 ORDER BY id DESC')
    entries = [dict(time=format_time(row[0]), printer=row[1], copies=row[2], success=row[3]) for row in cur.fetchall()]
    numreq = g.db.execute('SELECT COUNT(*) FROM Entries').fetchone()[0]
    dayreq = g.db.execute('SELECT COUNT(*) FROM Entries WHERE time > ?', [time.time()-86400]).fetchone()[0]
    return render_template('layout.html', entries=entries, numrequests=numreq, dayrequests=dayreq)

@app.route('/show', methods=['POST'])
def show_successful():
    return redirect(url_for('show_entries'))

@app.route('/clear', methods=['POST'])
def clear_database():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('delete from entries')
    g.db.commit()
    flash('Database cleared.')
    return redirect(url_for('show_entries'))

@app.route('/status', methods=['GET'])
def get_status():
    response = {}
    try:
        with open('/tmp/errors.txt', 'r') as f:
            message = f.readline()
            if len(message) > 0:
                response["errors"] = message
    except:
        pass
    response["printerPages"] = pickle.load(open("printerPages.p", "rb"))
    return(jsonify(**response))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
    return redirect(url_for('show_entries'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()