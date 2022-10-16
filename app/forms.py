'''
файл (модуль) для хранения классов веб-форм
'''

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User, Users


class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    # email removed
    # email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_login(self, login):
        user: User = Users.get_by_login(login.data)
        if user is not None:
            raise ValidationError('Please use a different username.')
        return

    '''
    # removed with email field
    def validate_email(self, email):
        user: User = Users.get_by_email(email.data)
        if user is not None:
            raise ValidationError('Please use a different email address.')
        return
    '''

