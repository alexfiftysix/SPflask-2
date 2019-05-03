# TODO: Allow re-ordering of videos/music
# TODO: Work out file upload (For bg photos for music)
# TODO: Generalize delete routes, video+music routes
# TODO: Don't actually have page by page navigation.
#       Have the one page include all info, but info is hidden/shown based on menu,
#       or scrolls down based on menu selection. Then mobile version will not need to be seperate


from excluded.config import config
from iframe_processing import valid_bandcamp

from flask import Flask, render_template, flash, redirect, session, request
from flask_sqlalchemy import SQLAlchemy
from data import contact_list
import datetime
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)
app.secret_key = config['secret']

# Config SQLalchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://{username}:{password}@{host}/{db_name}'.format(
    username=config['db_username'],
    password=config['db_password'],
    host=config['db_host'],
    db_name=config['db_name']
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_RECYCLE'] = 380
app.permanent_session_lifetime = datetime.timedelta(minutes=15)
db = SQLAlchemy(app)

contacts = contact_list()


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
    id = db.Column('id', db.SmallInteger, primary_key=True)
    title = db.Column('title', db.String(200), unique=True, nullable=False)
    iframe = db.Column('iframe', db.String(2000), nullable=False)

    def __repr__(self):
        return '<Title: %r>' % self.title


@app.route('/')
@app.route('/mobile')
def mobile():
    db.create_all()
    future_gigs_data = Gigs.query.filter(Gigs.date >= datetime.date.today()).order_by(Gigs.date).all()
    one_month_ago = datetime.date.today() - datetime.timedelta(days=28)
    past_gigs_data = Gigs.query.filter(Gigs.date < datetime.date.today()).filter(Gigs.date > one_month_ago).all()

    size = len(future_gigs_data) + len(past_gigs_data)

    music_data = Music.query.all()
    music_count = len(music_data)

    video_data = Videos.query.all()
    video_count = len(video_data)

    return render_template('mobile.html', mobile=True, gigs=future_gigs_data, old_gigs=past_gigs_data, gigs_num=size,
                           contacts=contacts, music_count=music_count, music_data=music_data, video_data=video_data,
                           video_count=video_count)


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

    if not valid_bandcamp(iframe):
        flash("make sure you've got the right iframe - has to be from street pieces bandcamp")
    elif len(title) > 200:
        flash('song title is too long. Must be <= 200 chars')
    elif len(iframe) > 2000:
        flash('iframe text is too long. Talk to the devs')
    else:
        to_add = Music(title=title, iframe=iframe)
        db.session.add(to_add)
        db.session.commit()

    return redirect('/')


class Videos(db.Model):
    __tablename__ = 'videos'
    id = db.Column('id', db.SmallInteger, primary_key=True)
    title = db.Column('title', db.String(150), unique=True, nullable=False)
    iframe = db.Column('iframe', db.String(2000), nullable=False)


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
    # TODO: Validate better
    if '<iframe' not in iframe:
        flash("That's not an iframe")
    elif 'youtube' not in iframe:
        flash("That's not from youtube")
    elif len(iframe) > 2000:
        flash("iframe too long")
    elif len(title) > 150:
        flash("Title must be <= 150 chars")
    else:
        to_add = Videos(title=title, iframe=iframe)
        db.session.add(to_add)
        db.session.commit()

    return redirect('/video')


class Gigs(db.Model):
    __tablename__ = 'gigs'
    id = db.Column('id', db.SmallInteger, primary_key=True)
    title = db.Column('title', db.String(250), unique=False, nullable=False)
    location = db.Column('location', db.String(250), unique=False, nullable=False)
    date = db.Column('date', db.Date, nullable=False)
    price = db.Column('price', db.DECIMAL(10, 2), nullable=False)
    link = db.Column('link', db.String(2000), nullable=True)


@app.route('/deleteGigs')
@is_logged_in
def delete_gigs():
    future_gigs_data = Gigs.query.filter(Gigs.date >= datetime.date.today()).all()
    past_gigs_data = Gigs.query.filter(Gigs.date < datetime.date.today()).order_by(Gigs.date.desc()).all()
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
    location = request.form['location']
    date = request.form['date']
    price = request.form['price']
    link = request.form['link']
    to_add = Gigs(title=title, location=location, date=date, price=price, link=link)
    db.session.add(to_add)
    db.session.commit()

    return redirect('/gigs')


@app.route('/addGig', methods=['GET'])
@is_logged_in
def add_gig():  # TODO: Add gig
    return render_template('addGig.html')


class Users(db.Model):
    username = db.Column('username', db.String(50), primary_key=True)
    password = db.Column('password', db.String(250), unique=False, nullable=False)


# TODO: Email contact at website bottom


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


# User login
@app.route('/login', methods=['POST'])
def login_submit():
    username = request.form['username']
    password_candidate = request.form['password']

    user = Users.query.filter_by(username=username).first()
    if user is None:
        app.logger.info('User does not exist')
        return redirect('/')
    if sha256_crypt.verify(password_candidate, user.password):
        session['logged_in'] = True
        session['username'] = username

        return redirect('/')
    else:
        app.logger.info('Password wrong')
        return redirect('/')


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')


if __name__ == '__main__':
    # TODO: Why this session_type business?
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(debug=True)
