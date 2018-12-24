## TODO: Migrate to SQLAlchemy

import os
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from data import gigs_list, contact_list
from flask_mysqldb import MySQL
from wtforms import Form, StringField, DecimalField, TextAreaField, PasswordField, validators, DateTimeField
from wtforms.fields.html5 import DateField

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
import flask_wtf

from passlib.hash import sha256_crypt
from functools import wraps
import datetime

app = Flask(__name__)
app.secret_key = 'secret123'

# Config SQLalchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/StreetPiecesClean'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Config mySQL (flask-mysql)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'  # TODO: hide this somehow?
app.config['MYSQL_DB'] = 'StreetPiecesClean'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # return from DB as dictionary
# Init mySQL
mysql = MySQL(app)

gig_list = gigs_list()
contacts = contact_list()


# TODO: Work out file upload (For bg photos for music)
# TODO: Generalize delete routes, video+music routes
# TODO: Make sessions expire after 1 hour or so

# check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')

    return wrap


class Music(db.Model):
    __tablename__ = 'music'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=True, nullable=False)
    iframe = db.Column(db.String(2000), unique=True, nullable=False)

    def __repr__(self):
        return '<Title: %r>' % self.title


@app.route('/')
@app.route('/music')
def music():
    db.create_all()
    data = Music.query.all()
    size = len(data)
    if size == 0:
        eyew = Music(title="Everything You Ever Wanted",
                     iframe='<iframe style="border: 0; width: 350px; height: 350px;" src="https://bandcamp.com/EmbeddedPlayer/album=77046358/size=large/bgcol=ffffff/linkcol=0687f5/minimal=true/transparent=true/" seamless><a href="http://streetpieces.bandcamp.com/album/everything-you-ever-wanted">Everything You Ever Wanted by Street Pieces</a></iframe>')
        other_side = Music(title="The Other Side",
                           iframe='<iframe style="border: 0; width: 350px; height: 350px;" src="https://bandcamp.com/EmbeddedPlayer/album=934170608/size=large/bgcol=ffffff/linkcol=0687f5/minimal=true/transparent=true/" seamless><a href="http://streetpieces.bandcamp.com/album/the-other-side">The Other Side by Street Pieces</a></iframe>')
        db.session.add(eyew)
        db.session.add(other_side)
        db.session.commit()
        data = Music.query.all()
        size = len(data)
    return render_template('music.html', music_players=data, size=size)


# TODO: use a DELETE request instead of this thing
@app.route('/deleteMusic/<music_id>')
@is_logged_in
def delete_music(music_id):
    to_delete = Music.query.filter_by(id=music_id).first()  # Can only be one, but don't want full object
    db.session.delete(to_delete)
    db.session.commit()
    return redirect('/music')


@app.route('/deleteMusic')
@is_logged_in
def delete_mus():
    data = Music.query.all()
    return render_template('deleteMusic.html', music=data)


@app.route('/addMusic')
@is_logged_in
def addMusicForm():
    return render_template('addMusic.html')


@app.route('/addMusic', methods=['POST'])
@is_logged_in
def addMusic():
    title = request.form['title']
    iframe = request.form['iframe']
    to_add = Music(title=title, iframe=iframe)
    db.session.add(to_add)
    db.session.commit()

    return redirect('/')


class Videos(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True, nullable=False)
    iframe = db.Column(db.String(2000), unique=True, nullable=False)


@app.route('/video')
def video():
    db.create_all()

    data = Videos.query.all()
    size = len(data)
    if size == 0:
        monster = Videos(title="Monster",
                         iframe='<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/uL-RIv0HP3s" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>')
        bkow = Videos(title="BKOW Lyric Video",
                      iframe='<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/-NF9rxqJB8o" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>')
        db.session.add(monster)
        db.session.add(bkow)
        db.session.commit()
        data = Videos.query.all()
        size = len(data)

    return render_template('video.html', videos=data, size=size)


@app.route('/deleteVideo')
@is_logged_in
def delete_vid():
    data = Videos.query.all()
    return render_template('deleteVideo.html', videos=data)


@app.route('/deleteVideo/<vid_id>')
@is_logged_in
def delete_video(vid_id):
    to_delete = Videos.query.filter_by(id=vid_id).first()  # Can only be one, but don't want full object
    db.session.delete(to_delete)
    db.session.commit()

    return redirect('/video')


@app.route('/addVideo', methods=['GET'])
@is_logged_in
def add_video():
    return render_template('addVideo.html')


@app.route('/addVideo', methods=['POST'])
@is_logged_in
def add_video_for_real():
    title = request.form['title']
    iframe = request.form['iframe']
    to_add = Videos(title=title, iframe=iframe)
    db.session.add(to_add)
    db.session.commit()

    return redirect('/video')


class Gigs(db.Model):
    __tablename__ = 'gigs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=False, nullable=False)
    location = db.Column(db.String(250), unique=False, nullable=False)
    date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    link = db.Column(db.String(2000), nullable=True)


@app.route('/gigs')
def gigs():
    db.create_all()

    # TODO: Sort by date
    future_gigs_data = Gigs.query.filter(Gigs.date >= datetime.date.today()).all()
    past_gigs_data = Gigs.query.filter(Gigs.date < datetime.date.today()).all()  # TODO: Don't allow super-old dates
    size = len(future_gigs_data) + len(past_gigs_data)

    return render_template('gigs.html', gigs=future_gigs_data, old_gigs=past_gigs_data, gigs_num=size)


@app.route('/deleteGigs')
@is_logged_in
def delete_gigs():
    future_gigs_data = Gigs.query.filter(Gigs.date >= datetime.date.today()).all()
    past_gigs_data = Gigs.query.filter(Gigs.date < datetime.date.today()).all()  # TODO: Don't allow super-old dates
    return render_template('deleteGigs.html', gigs=future_gigs_data, old_gigs=past_gigs_data)


@app.route('/deleteGig/<gig_id>')
@is_logged_in
def delete_gig(gig_id):
    to_delete = Gigs.query.filter_by(id=gig_id).first()  # Can only be one, but don't want full object
    db.session.delete(to_delete)
    db.session.commit()

    return redirect('/gigs')


@app.route('/addGig', methods=['POST'])
@is_logged_in
def add_gig_for_real():  # TODO: Addd gig
    title = request.form['title']
    location= request.form['location']
    date = request.form['date']
    price = request.form['price']
    link = request.form['link']
    to_add = Gigs(title=title, location=location, date=date, price=price, link=link)
    db.session.add(to_add)
    db.session.commit()

    return redirect('/gigs')


@app.route('/contact')
def contact():
    return render_template('contact.html', contacts=contacts)


@app.route('/addGig', methods=['GET'])
@is_logged_in
def add_gig():  # TODO: Addd gig
    return render_template('addGig.html')


class NewUserForm(Form):
    username = StringField('Username', [validators.Length(min=1, max=250)])
    password = PasswordField('Password', [
        validators.data_required(),
        validators.Length(min=8, max=250)
    ])
    confirm = PasswordField('Confirm Password')


# TODO: Get user routes on SQLAlchemy
@app.route('/addUser', methods=['GET', 'POST'])
@is_logged_in
def add_user():
    form = NewUserForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create Cursor
        cur = mysql.connection.cursor()

        # Insert new user
        cur.execute('INSERT INTO users(username, password) VALUES(%s, %s)', (username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        mysql.connection.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('/music'))
    return render_template('addUser.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form fields
        # not using wtForms
        username = request.form['username']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute('SELECT * FROM users WHERE username = %s', [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed

                session['logged_in'] = True
                session['username'] = username

                return redirect('/')
            else:
                app.logger.info('PASSWORD INCORRECT')
                error = 'Username or password incorrect'
                return render_template('login.html', error=error)

        else:
            error = 'Username or password incorrect'
            app.logger.info('NO USER')
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')


if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(debug=True)
