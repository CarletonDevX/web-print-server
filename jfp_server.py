#Adapted from the "flaskr" tutorial at http://flask.pocoo.org/

import sqlite3
import os, time, datetime
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from contextlib import closing

# configuration
DATABASE = '/var/www/web-print-server/web-print-server/db/data.db'
DEBUG = True
SECRET_KEY = 'keepitsecretkeepitsafe'
USERNAME = 'devx'
PASSWORD = 'devx'


app = Flask(__name__)
app.config.from_object(__name__)

printerPages = {
  "print\\CASS101-X4600": 1,
  "print\\CLST100-CC5051": 1,
  "print\\CMC020-CC5051":  1,
  "print\\CMC104-CC5051":  1,
  "print\\CMC104-Gray-CC5051": 1,
  "print\\CMC121H-CC5051": 1,
  "print\\CMC201-X4600": 1,
  "print\\CMC305-X4600": 1,
  "print\\COWL108-CC5051": 1,
  "print\\FACI318-CC5051": 1,
  "print\\GHUE156-X5550":  1,
  "print\\GOOD102-X3610":  1,
  "print\\GOOD103-CC5051": 1,
  "print\\GOOD103-X6350":  1,
  "print\\HOPN104-CC5051": 1,
  "print\\HUL007A-X3600":  1,
  "print\\HUL010-X3600": 1,
  "print\\HUL014-X6350": 1,
  "print\\HUL100-CC5051":  1,
  "print\\LAIR115-CC5051": 1,
  "print\\LAIR118-CC5051": 1,
  "print\\LAIR208-CC5051": 1,
  "print\\LAIR208-X4600":  1,
  "print\\LAIR300-X3610":  1,
  "print\\LAST110-CC5051": 1,
  "print\\LDC220-CC5051":  2,
  "print\\LDC243-X5550": 2,
  "print\\LEIG128-LJM602": 2,
  "print\\LEIG217-X4510":  2,
  "print\\LEIG218-CC5051": 2,
  "print\\LEIG218-Gray-CC5051":  2,
  "print\\LEIG231-X4600":  2,
  "print\\LEIG326-CC5051": 2,
  "print\\LEIG326-X4600":  2,
  "print\\LEIG414-LJM602": 2,
  "print\\LIBR-Public-X5550":  2,
  "print\\LIBR400-CC5051": 2,
  "print\\MUDD075-X4510":  2,
  "print\\MUDD169-X4600":  2,
  "print\\MUSI200-X4600":  2,
  "print\\OLIN007-X6350":  2,
  "print\\OLIN011-X3600":  2,
  "print\\OLIN104-X4510":  2,
  "print\\OLIN112-X4510":  2,
  "print\\OLIN125-CC5051": 2,
  "print\\OLIN125-Gray-CC5051":  2,
  "print\\OLIN215-CC5051": 2,
  "print\\OLIN301-X4600":  2,
  "print\\OLIN311-CC5051": 2,
  "print\\OLIN311-X6350":  2,
  "print\\RSC105-CC5051":  3,
  "print\\RSC235-CC5051":  3,
  "print\\SAYL-Public-X5550":  3,
  "print\\SAYL050-X6360":  3,
  "print\\SAYL057-CC5051": 3,
  "print\\SAYL109A-X4510": 3,
  "print\\SAYL150-X4510":  3,
  "print\\SCOV014-CC5051": 3,
  "print\\SEVY014-CC5051": 3,
  "print\\SEVY129-CC5051": 3,
  "print\\STRG107-CC5051": 3,
  "print\\TWCO100-CC5051": 3,
  "print\\WCC003-X3610": 3,
  "print\\WCC028-CC5051":  3,
  "print\\WCC138-X6360": 3,
  "print\\WCC146-X3610": 3,
  "print\\WCC225-CC5051":  3,
  "print\\WEST200-CC5051": 3,
  "print\\WILL119-X4600":  3,
  "print\\WILL310-CC5051": 3,
  "print\\WILL409-X4600":  3
}

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
    response["printerPages"] = printerPages
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