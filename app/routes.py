# -*- coding: utf-8 -*-
'''
файл функций просмотра (файл представлений)
'''

from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app import app
from app.forms import LoginForm, RegistrationForm
from app.models import Users, User


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'maks-ti'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        },
        {
            'author': {'username': 'Ипполит'},
            'body': 'Какая гадость эта ваша заливная рыба!!'
        }
    ] # mock obj
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    '''
    validate_on_submit: 
    GET - вернёт False
    POST - проверит форму на корректность (проверяет валидаторы)
    если коректно - True
    если некоректно - False
    '''
    if form.validate_on_submit():
        user: User = Users.get_by_username(form.username.data) # получение объекта пользователя
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    '''рендер страницы sign in'''
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user: User = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        # добавляем нового пользователя в базу
        Users.add(user)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user: User = Users.get_by_username(username)
    if user is None:
        abort(404)
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'},
    ] # mock obj
    return render_template('user.html', user=user, posts=posts)



#chcp 1251
#PATH C:\Program Files\PostgreSQL\14\bin;%PATH%
#psql -h localhost -p 5432 -d weather_parser -U maxti
#C:\Users\maxti\PycharmProjects\messenger>venv\Scripts\activate



