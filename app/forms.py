'''
файл (модуль) для хранения классов веб-форм
'''

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError,  EqualTo, Length
from app.models import User, Users


class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
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


class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    about = TextAreaField('About me', validators=[Length(min=0, max=300)])
    biography = TextAreaField('Biography', validators=[Length(min=0, max=2000)])
    image = FileField('Profile image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    title = TextAreaField('Post title', validators=[Length(min=1, max=200)])
    post_text = TextAreaField('Post text', validators=[Length(min=1, max=100000)])
    image = FileField('Post image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Submit')


class MessageForm(FlaskForm):
    text = TextAreaField('Message text', validators=[Length(min=1, max=1000)])
    submit = SubmitField('Send')


class CommentForm(FlaskForm):
    text = TextAreaField('Comment text', validators=[Length(min=1, max=200)])
    submit = SubmitField('Send')


class SearchForm(FlaskForm):
    text = StringField('Search string', validators=[DataRequired()])
    submit = SubmitField('Search')


class ChatForm(FlaskForm):
    chat_name = StringField('Chat name', validators=[DataRequired()])
    users = SelectMultipleField('Users', coerce=int)
    submit = SubmitField('Create chat')

