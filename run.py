# -*- coding: utf-8 -*-
# imports
import os
import sqlite3
from flask import Flask, session, request, g, redirect, url_for, \
 abort, render_template, flash, jsonify, escape, flash
 
# konfigurasjon av globale variable

DEBUG = True
SECRET_KEY = 'Qh\x84J\xbb^\xeb\x8d\x96\x07\xa1\xf2Q\x905(\xbca\x06\x13\x1a\xb5\xf6\xad'

music_dir = '/Users/Eirik/myproject/prosjekt/static/music'
video_dir = '/Users/Eirik/myproject/prosjekt/static/video'
image_dir = 'Users/Eirik/myproject/prosjekt/static/image'

# lager og initialiserer app’en
app = Flask(__name__)
app.config.from_object(__name__)
@app.route('/', methods=['GET', 'POST'])

def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
          error = 'Feil innlogging'
        else:
          session['logged_in'] = True
          flash('Du er nå innlogget!')
          return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('logged_in', None)
    flash('Du er nå logget ut!')
    return redirect(url_for('login'))

def index():
    """Leter etter data i databasen og viser de."""
    return render_template('index.html', entries=entries)

@app.route('/registrer.html')
def index():
    return render_template('registrer.html')


if __name__ == '__main__':
    app.run(debug=True)