
import os
import sqlite3
from flask import Flask, render_template, flash, request, session, url_for, redirect, g, \
    escape, abort, jsonify
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from flask.ext.googlemaps import GoogleMaps
from flask.ext.sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import gc

# konfigurasjon av globale variable
DATABASE = 'alpinklubben.db'
DEBUG = True
SECRET_KEY = 'Qh\x84J\xbb^\xeb\x8d\x96\x07\xa1\xf2Q\x905(\xbca\x06\x13\x1a\xb5\xf6\xad'

# lager og initialiserer appen
app = Flask(__name__)
GoogleMaps(app)
app.config.from_object(__name__)
@app.route('/', methods=['GET', 'POST'])


@app.route('/')
def homepage():
    return render_template("forside.html")

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/kontaktoss')
def kontaktoss():
    return render_template("kontaktoss.html")



class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.Required(),
    validators.EqualTo('confirm', message="Passordene er ikke like.")])
    confirm = PasswordField('Gjenta Passord')

@app.route('/registrer', methods=['GET','POST'])
def registrer_side():
    try:
        form = RegistrationForm(request.form)
        db = get_db()
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            
            x = db.execute('''SELECT * FROM users WHERE username = ?''',
			(username,))
            if x.fetchone():
                flash("Dette brukernavnet eksisterer - velg et annet")
                return render_template('registrer.html', form=form)
            else:
                db.execute('''INSERT INTO users(username, email, password) VALUES(?, ?, ?)''',
                (username, email, password))
                db.commit()
                flash('Takk for at du registrerte deg')
                gc.collect()

                session['logget_inn'] = True
                session['username'] = username
                flash('Du er logget inn som:'+str(session['username']))

                return redirect(url_for('index'))
        return render_template("registrer.html", form=form)
    except Exception as e:
        return (str(e))


	
	
@app.route('/login', methods = ['GET','POST'])
def login_page():
    error = ''
    try:
        db = get_db()
        if request.method == "POST":
            c = db.execute('SELECT * FROM users WHERE username = ?',
            (request.form['username'],))
            c = c.fetchone()[3]
			
            if sha256_crypt.verify(request.form['password'], c):
                session['logget_inn'] = True
                session['username'] = request.form['username']
                flash("You are now logged in")
                return redirect(url_for('index'))

            else:
                error = "Ugyldig innlogging - prov igjen."

        gc.collect()
        return render_template("login.html", error=error)
	
    except Exception as e:
#       flash(e) - error handling
        flash('Ugyldig innlogging')
        return render_template("login.html", error = error)

@app.route('/loggut')
def logout():
	session.pop('logged_in', None)
	session.clear()
	flash('You have been logged out.')
	gc.collect()
	return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(405)
def method_not_found(e):
    return render_template("405.html")

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logget_inn' in session:
            return f(*args, **kwargs)
        else:
            flash('Du maa logge inn for aa se denne siden')
            return redirect(url_for('login_page'))
    return wrap

@app.route('/utleie', methods = ['GET','POST'])
@login_required
def utleie():
    error = ''
    try:
        db = get_db()
        if request.method == "POST":
            pakke = request.form.get('optionsRadios', '')
            alder = 'tileggbox' in request.form
            leietid = request.form['leietid']
            leieantall = request.form['leieantall']
            if not pakke:
                flash('Vennligst velg en pakke')
                return render_template("utleie.html", error = error)
            else:
                db.execute('''INSERT INTO utleie(pakke, alder, leietid, leieantall) VALUES(?, ?, ?, ?)''',
                (pakke, alder, leietid, leieantall))
                db.commit()
#                flash('Takk for ditt kjop')
                gc.collect()
                return redirect(url_for('oppsummering'))

        else:
            return render_template("utleie.html", error = error)
    except Exception as e:
        return (str(e))

@app.route('/oppsummering')
@login_required
def oppsummering():
    db = get_db()
    cur = db.execute('''SELECT * FROM utleie WHERE id = (SELECT MAX(id) FROM utleie)''')
    utleies = cur.fetchall()
    return render_template('oppsummering.html', utleies=utleies)


@app.route('/heiskort')
@login_required
def heiskort():
    return render_template('heiskort.html')


# kobler til databasen
def connect_db():
    """Kobler til databasen."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv
 
# lager databasen
def init_db():
    with app.app_context():
      db = get_db()
      with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
      db.commit()
	
# aapner forbindelsen til databasen
def get_db():
    if not hasattr(g, 'sqlite_db'):
      g.sqlite_db = connect_db()
    return g.sqlite_db
 
# lukker forbindelsen til databasen
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
      g.sqlite_db.close()

if __name__ == "__main__": #Kanskje bruke login her?
    init_db()
    app.run(debug=True)