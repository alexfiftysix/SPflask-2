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


class NewVideoForm(Form):
    name = StringField('Title', [validators.data_required(), validators.Length(min=1, max=100)])
    url = StringField('iframe', [validators.data_required(), validators.Length(min=1, max=500)])


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


@app.route('/gigs')
def gigs():
    cur = mysql.connection.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS gigs (
                title varchar(250), 
                location varchar(250), 
                date DATETIME, 
                price int, 
                link varchar(2000)); """)

    future_gigs = cur.execute('SELECT * FROM gigs WHERE DATE >= CURDATE()')
    future_gigs_data = sorted(cur.fetchall(), key=lambda k: k['date'])

    past_gigs = cur.execute('SELECT * FROM gigs WHERE DATE >= CURDATE() - INTERVAL 1 WEEK AND DATE < CURDATE()')
    past_gigs_data = sorted(cur.fetchall(), key=lambda k: k['date'])

    gigs_num = future_gigs + past_gigs

    return render_template('gigs.html', gigs=future_gigs_data, old_gigs=past_gigs_data, gigs_num=gigs_num)
    # TODO: Work out what to do if no gigs
    # Close connection


@app.route('/deleteGigs')
@is_logged_in
def delete_gigs():
    cur = mysql.connection.cursor()

    result = cur.execute('SELECT * FROM gigs WHERE DATE >= CURDATE() - INTERVAL 1 WEEK')

    future_gigs = cur.execute('SELECT * FROM gigs WHERE DATE >= CURDATE()')
    future_gigs_data = sorted(cur.fetchall(), key=lambda k: k['date'])

    past_gigs = cur.execute('SELECT * FROM gigs WHERE DATE >= CURDATE() - INTERVAL 1 WEEK AND DATE < CURDATE()')
    past_gigs_data = sorted(cur.fetchall(), key=lambda k: k['date'])

    return render_template('deleteGigs.html', gigs=future_gigs_data, old_gigs=past_gigs_data)


@app.route('/deleteGig/<gig_id>')
@is_logged_in
def delete_gig(gig_id):
    print(gig_id)
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM gigs WHERE id = %s", [gig_id])
    mysql.connection.commit()
    return redirect('/gigs')


@app.route('/contact')
def contact():
    return render_template('contact.html', contacts=contacts)


@app.route('/photos')
@is_logged_in
def photos():
    return render_template('photos.html')


class NewPhotoForm(FlaskForm):
    path = FileField('Photo', validators=[FileRequired()])


@app.route('/addPhoto', methods=['GET', 'POST'])
@is_logged_in
def add_photo():
    form = NewPhotoForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        f = form.path.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(
            app.instance_path, 'static/images/gallery', filename
        ))

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO photos(path) VALUES(%s)', filename)
        mysql.connection.commit()
        mysql.connection.close()

        return redirect('photos.html')
    return render_template('addPhoto.html', form=form)


class NewGigForm(Form):
    title = StringField('Title', [validators.data_required(), validators.Length(min=1, max=250)])
    location = StringField('Location', [validators.data_required(), validators.Length(min=1, max=250)])
    date = DateField('Date', [validators.data_required()])
    price = DecimalField('Price', [validators.data_required()])
    link = StringField('Link', [validators.Length(min=0, max=250)])


@app.route('/addGig', methods=['GET', 'POST'])
@is_logged_in
def add_gig():
    form = NewGigForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        location = form.location.data
        date = form.date.data
        price = form.price.data
        link = form.link.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Insert new user
        cur.execute('INSERT INTO gigs(title, location, date, price, link) VALUES(%s, %s, %s, %s, %s)',
                    [title, location, date, price, link])

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        mysql.connection.close()

        return redirect('/gigs')
        return render_template('addGig.html', form=form)  # todo: replace this
    return render_template('addGig.html', form=form)


class NewUserForm(Form):
    username = StringField('Username', [validators.Length(min=1, max=250)])
    password = PasswordField('Password', [
        validators.data_required(),
        validators.Length(min=8, max=250)
    ])
    confirm = PasswordField('Confirm Password')


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
