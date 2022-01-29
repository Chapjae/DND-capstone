from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField
from wtforms import validators
from wtforms.validators import InputRequired

class UserForm(FlaskForm):
    username = StringField("Username", validators = [InputRequired()])
    password = PasswordField("Password", validators = [InputRequired()])

class CharacterForm(FlaskForm):
    charName = StringField("Character Name", validators = [InputRequired()])
    charClass = SelectField("Character Class", choices=[], validators = [InputRequired()])
    charLevel = IntegerField("Character Level", validators = [InputRequired()])
    charRace = StringField("Character Race", validators=[InputRequired()])