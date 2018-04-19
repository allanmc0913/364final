# Import statements
import os
import requests
import json
import requests_oauthlib
import webbrowser
import json

from flask import Flask, render_template, session, redirect, request, url_for, flash
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, PasswordField, BooleanField, SelectMultipleField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from werkzeug.security import generate_password_hash, check_password_hash

# Imports for login management
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Application configurations
app = Flask(__name__)
app.debug = True
app.use_reloader = True
app.config['SECRET_KEY'] = 'hardtoguessstring'
app.config[
    "SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/final364"
#postgresql://localhost/final364
#postgres://axakfrrkqriatf:d9618497f55fc5c18080a5ddfb7b826127021c5bcdf48fe264e81e9ad10a5445@ec2-54-163-240-54.compute-1.amazonaws.com:5432/d5pm76di938fk


app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# App addition setups
manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

# Login configurations setup
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)  # set up login manager

########################
######## Models ########
########################


##Association Tables##

#association table between search term and tweets
search_tweets = db.Table('search_tweets', db.Column('search_id', db.Integer, db.ForeignKey('searchterm.id')),
                       db.Column('tweet_id', db.Integer, db.ForeignKey('tweet.id')))

#association table between tweets and user collections
user_collection = db.Table('user_collection', db.Column('tweet_id', db.Integer, db.ForeignKey('tweet.id')),
                           db.Column('personaltweetcollection_id', db.Integer, db.ForeignKey('personaltweetcollection.id')))

## User-related Models

# Special model for users to log in

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    tweets = db.relationship('PersonalTweetCollection', backref='User')


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


## DB load function
## Necessary for behind the scenes login manager that comes with flask_login capabilities! Won't run without this.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # returns User object or None


# Model to store tweets
class Tweet(db.Model):
    __tablename__ = "tweet"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text())

    def __repr__(self):
        return "The tweet text is: {}".format(self.title)


# Model to store a personal tweet collection
class PersonalTweetCollection(db.Model):

    __tablename__ = "personaltweetcollection"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


    User_id = db.Column(db.Integer, db.ForeignKey('users.id'))


    tweets = db.relationship('Tweet', secondary=user_collection,
                           backref=db.backref('personaltweetcollection', lazy='dynamic'), lazy='dynamic')


class SearchTerm(db.Model):

    __tablename__ = "searchterm"
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(256))

    tweets = db.relationship('Tweet', secondary=search_tweets, backref=db.backref('searchterm', lazy='dynamic'),
                           lazy='dynamic')


    def __repr__(self):
        return "{}".format(self.term)


########################
######## Forms #########
########################

# Provided
class RegistrationForm(FlaskForm):
    email = StringField('Email:', validators=[Required(), Length(1, 64), Email()])
    username = StringField('Username:', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                                      'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password:', validators=[Required(), EqualTo('password2', message="Passwords must match")])
    password2 = PasswordField("Confirm Password:", validators=[Required()])
    submit = SubmitField('Register User')

    # Additional checking methods for the form
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken')


# Provided
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class TweetSearchForm(FlaskForm):
    search = StringField("Enter a hashtag to search tweets (leave out #)", validators=[Required()])
    submit = SubmitField('Submit')

    def validate_search(self, field):
        if field.data.startswith('#'):
            raise ValidationError("Please leave out #")

class CollectionCreateForm(FlaskForm):
    name = StringField('Collection Name', validators=[Required()])
    tweet_picks = SelectMultipleField('Tweets to include', coerce=int)
    submit = SubmitField("Create Collection")

    def validate_name(self, field):
        if len(field.data) == 0:
            raise ValidationError("Collection Name must not be empty!")


class DeleteButtonForm(FlaskForm):
    submit = SubmitField('Delete')


###############################
######## Helper Funcs #########
###############################

##This code to connect to Twitter is taken from SI106's textbook (I tutor students in SI106)
##https://www.programsinformationpeople.org/runestone/static/publicPIP/APIsWithOAuth/TwitterAPI.html#using-the-provided-code-for-the-twitter-api
##The code is provided in the textbook dealing with OAuth and Twitter in their new v1.1

def get_api_data(hashtag):

    f = open("creds.txt", 'r')
    (client_key, client_secret, resource_owner_key, resource_owner_secret, verifier) = json.loads(f.read())
    f.close()

    hashtag = "%23" + hashtag
    protected_url = 'https://api.twitter.com/1.1/account/settings.json'
    oauth = requests_oauthlib.OAuth1Session(client_key,
                            client_secret=client_secret,
                            resource_owner_key=resource_owner_key,
                            resource_owner_secret=resource_owner_secret)

    r = oauth.get("https://api.twitter.com/1.1/search/tweets.json", params = {'q': str(hashtag), 'count' : 5})

    res = r.json()

    f = open('nested.txt', 'w')
    f.write(json.dumps(res))
    f.close()

    f = open('nested.txt', 'r')
    temp = json.loads(f.read())
    statuses = temp['statuses']
    return statuses

def get_tweet_by_id(id):
    t = Tweet.query.filter_by(id=id).first()
    return t

def get_or_create_tweet(text):
    tweet = Tweet.query.filter_by(text=text).first()
    if not tweet:
        new_tweet = Tweet(text=text)
        db.session.add(new_tweet)
        db.session.commit()
        return new_tweet
    else:
        return tweet

def get_or_create_search_term(hashtag):
    search = SearchTerm.query.filter_by(term=hashtag).first()
    if not search:
        new_hashtag = SearchTerm(term=hashtag)
        db.session.add(new_hashtag)
        db.session.commit()

        tweetList = get_api_data(str(hashtag))
        for tweet in tweetList:
            tweet_return = get_or_create_tweet(tweet['text'])
            new_hashtag.tweets.append(tweet_return)
        return new_hashtag
    else:
        return hashtag

def get_or_create_collection(name, current_user, tweet_list=[]):
    user_id = User.query.filter_by(username=current_user).first().id
    collection = PersonalTweetCollection.query.filter_by(name=name, User_id=user_id).first()
    if not collection:
        new_collection = PersonalTweetCollection(name=name, User_id=user_id)
        db.session.add(new_collection)
        db.session.commit()
        for tweet in tweet_list:
            new_collection.tweets.append(tweet)
        return new_collection
    else:
        return collection


########################
#### View functions ####
########################

## Error handling routes
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#Login route, displays login form, queries database to see if email exists, verifies password, and if all goes well, redirects to index
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

#Logout, redirect to index
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("index"))

#Register, invoke registration form, and add new user to db, redirect to index
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now log in!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/secret')
@login_required
def secret():
    return "Only authenticated users can do this! Try to log in or contact the site admin."

#Route shows index page with inherited nav bar -- should show hashtag search form and then get_create the search term, redirect to search results
@app.route('/', methods=['GET', 'POST'])
def index():
    form = TweetSearchForm()
    if request.method == "POST" and form.validate_on_submit():
        tag = form.search.data
        term = get_or_create_search_term(tag)
        return redirect(url_for("search_results", search_term=term))

    return render_template('index.html', form=form)

#Route to return all the tweets from any given hashtag
@app.route('/tweets_searched/<search_term>')
def search_results(search_term):
    hashtag = SearchTerm.query.filter_by(term=search_term).first()
    relevant_tweets = hashtag.tweets.all()
    return render_template('searched_tweets.html', tweets=relevant_tweets, term=hashtag)

#Route to return all the search hashtags by querying search_term db
@app.route('/search_terms')
def search_terms():
    all_terms = SearchTerm.query.all()
    return render_template("search_terms.html", all_terms=all_terms)

#Route to return ALL tweets by querying tweets db
@app.route('/all_tweets')
def all_tweets():
    tweets = Tweet.query.all()
    return render_template('all_tweets.html', all_tweets=tweets)


#Route to create a collection of tweets and then pick tweets to add to collection through form, redirect once collection made to view collections
@app.route('/create_collection', methods=["GET", "POST"])
@login_required
def create_collection():
    form = CollectionCreateForm()
    tweets = Tweet.query.all()
    choices = [(t.id, t.text) for t in tweets]
    form.tweet_picks.choices = choices

    if form.validate_on_submit():
        name = form.name.data
        user_choices = form.tweet_picks.data

        tweet_lst = []

        for id in user_choices:
            obj = get_tweet_by_id(id)
            tweet_lst.append(obj)
        get_or_create_collection(name=name, current_user=current_user.username, tweet_list=tweet_lst)
        return redirect(url_for('collections'))
    return render_template('create_collection.html', form=form)

#Route to view all of a user's collections by querying personaltweetcollections by current user id
@app.route('/collections', methods=["GET", "POST"])
@login_required
def collections():
    form = DeleteButtonForm()
    collections = PersonalTweetCollection.query.filter_by(User_id=current_user.id).all()
    return render_template("collections.html", collections=collections, form=form)


#Route to view any collection by id without logging in, query personaltweetcollection by collection id number
@app.route('/collection/<id_num>')
def single_collection(id_num):
    id_num = int(id_num)
    collection = PersonalTweetCollection.query.filter_by(id=id_num).first()
    tweets=collection.tweets.all()
    return render_template('collection.html', collection=collection, tweets=tweets)

#Route to delete a collection, must sign in first, delete from PersonalTweetCollections table
@app.route('/delete/<id_num>', methods=["GET", "POST"])
@login_required
def delete(id_num):
    id_num = int(id_num)
    collection = PersonalTweetCollection.query.filter_by(id=id_num).first()
    db.session.delete(collection)
    db.session.commit()
    flash("Deleted Collection!")
    return redirect(url_for('collections'))



if __name__ == '__main__':
    db.create_all()
    app.run()
