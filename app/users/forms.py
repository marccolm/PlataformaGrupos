from flask.ext.wtf import Form
from flask_wtf.file import FileField, FileAllowed
from wtforms import TextField, HiddenField, RadioField, BooleanField, \
        SubmitField, IntegerField, FormField, StringField, PasswordField
from wtforms import validators, ValidationError
from wtforms.validators import Required, EqualTo, DataRequired, Length, Regexp
from wtforms.widgets import Input
from ..models import User

class RegistrationForm(Form):
    username = TextField('Username', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    first_name = TextField('First name', validators=[Required(), Length(1, 64)])
    last_name = TextField('Last name', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required(), EqualTo('confirm_password', message='Passwords must match.')])
    confirm_password = PasswordField('Confirm password', validators=[Required()])
    profile_picture = FileField('Profile picture', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Register')


class LoginForm(Form):
	username = TextField('Username', validators=[Required()])
	password = PasswordField('Password', validators=[Required()])
	remember_me = BooleanField('Remember me')
	submit = SubmitField('Login')

class EditProfileInfoForm(Form):
    username = TextField('Username', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    first_name = TextField('First name', validators=[Required(), Length(1, 64)])
    last_name = TextField('Last name', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[EqualTo('confirm_password', message='Passwords must match.')])
    confirm_password = PasswordField('Confirm password', validators=[])
    profile_picture = FileField('Profile picture', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    current_password = PasswordField('Current password', validators=[Required()])
    submit = SubmitField('Register')