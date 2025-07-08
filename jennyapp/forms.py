from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import FileField, StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, DataRequired, Length, EqualTo

ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp']

class RegisterForm(FlaskForm):
    email = StringField('Username', validators=[InputRequired(), Length(min=4, max=120)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=120)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired('Password is required'), EqualTo('password')])
    specialty = StringField('Specialty', validators=[InputRequired(), Length(min=4, max=120)])
    remember = BooleanField('Remember Me')
    # submit = SubmitField('Login')

class LoginForm(FlaskForm):
    email = StringField('Username', validators=[InputRequired(), Length(min=4, max=120)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=120)])
    remember = BooleanField('Remember Me')
    # submit = SubmitField('Login')