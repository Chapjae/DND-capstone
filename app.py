import os, pdb, requests
from re import L
from flask import Flask, render_template, flash, redirect, session, request, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from forms import UserForm, CharacterForm
from models import Character, db, connect_db, User

CURR_USER_KEY = "curr_user"

API_BASE_URL = "https://www.dnd5eapi.co/api/"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///dnd'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)


connect_db(app)

response = requests.get(API_BASE_URL)

@app.before_request
def add_user_to_g():
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
        
    else:
        g.user = None

def do_login(user):
    session[CURR_USER_KEY] = user.id

def do_logout():
    if CURR_USER_KEY in session :
        del session[CURR_USER_KEY]

@app.route('/')
def home_page():
    logged_in = 'user_id' in session
    #form = CharacterForm()
    #if form.validate_on_submit():
    #    charName = form.charName.data
    #    charClass = form.charClass.data
    #    charLevel = form.charLevel.data
    #    charRace = form.charRace.data
    #    new_character = CharSheet(charName=charName, charClass=charClass, charLevel=charLevel, charRace=charRace, user_id=session['user_id'])
    #    db.session.add(new_character)
    #    db.session.commit()
    #    flash("Character Created!", "success")
    #    return redirect('/characters')
    #if 'user_id' not in session:
    #    flash("You must login first", "danger")
    #   return redirect('/')
    
    return render_template("index.html", logged_in=logged_in)

@app.route("/register", methods = ["GET", "POST"])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        new_user = User.register(username, password)

        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        flash("Welcome! Create a Character to Begin Your Adventure!", "success")
        return redirect('/')
    
    return render_template('/register.html', form=form)

@app.route("/login", methods = ["GET", "POST"])
def login_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome back, {user.username}!", "primary")
            session['user_id'] = user.id
            return redirect('/characters')
        else:
            form.username.errors = ['Invalid username/password.']
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop("user_id")
    flash("We await your return!", "info")
    return redirect('/')

@app.route('/create', methods = ["GET", "POST"])
def create_character():
    if 'user_id' not in session:
        flash("You must login first", "danger")
        return redirect('/')
    logged_in = 'user_id' in session
    form = CharacterForm()

    form_choices = requests.get(f"{API_BASE_URL}classes")
    classes = jsonify(form_choices)

    form.classes.choices = [CharacterForm.charClass.data]
    if form.validate_on_submit():
        charName = form.charName.data
        charClass = api_classes
        charLevel = form.charLevel.data
        charRace = form.charRace.data
        new_character = Character(charName=charName, charClass=charClass, charLevel=charLevel, charRace=charRace, user_id=session['user_id'])

        db.session.add(new_character)
        db.session.commit()
       
        flash("Character Created! Create Another?", "success")
        return redirect('/create')

    return render_template("create.html", form=form, logged_in=logged_in)

@app.route('/characters/', methods=["GET", "POST"])
def show_characters():
    if 'user_id' not in session:
        flash("You must login first", "danger")
        return redirect('/')
    logged_in = 'user_id' in session
    characters = Character.query.all()
    return render_template("characters.html", logged_in=logged_in, characters=characters)

@app.route('/characters/<int:user_id>', methods=["GET", "POST"])
def your_characters(user_id):
    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('login')
    user = User.query.get_or_404(user_id)
    characters = Character.query.filter_by(user_id = user_id)
    if Character.user_id == session["user_id"]:
        db.session.delete(characters)
        db.session.commit()
        flash("Character Deleted", "info") 
        return redirect('/characters')
    flash("That is not your character", "danger")
    return redirect ('/characters')