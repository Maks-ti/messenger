# -*- coding: utf-8 -*-
'''
файл функций просмотра (файл представлений)
'''

from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app import app
from app.forms import LoginForm, RegistrationForm
# наверноепроще просто заимпортить все модели предваритеьно установив моификаторы доступа rpotected на те которые импортить не надо (или определить функцию импорта)
from app.models import User, Profile, Chat, Message, Post, Comment
from app.models import Users, Profiles, Follows, Chats, User_in_chat, Messages, Posts, Comments



@app.route('/')
@app.route('/index')
@login_required
def index():
    '''
    условно домашняя страница
    с лентой новостей (из постов юзеров на которых
    текущий юзер подписан
    '''
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
        # получение объекта пользователя
        user: User = Users.get_by_login(form.login.data)
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
        user: User = User(login=form.login.data, name=form.name.data)
        user.set_password(form.password.data)
        # добавляем нового пользователя в базу
        Users.add(user)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<login>')
@login_required
def user(login):
    user: User = Users.get_by_login(login)
    if user is None:
        abort(404)
    # получаем посты из базы
    posts = Posts.get_posts_by_user_id(user.id)
    return render_template('user.html', user=user, posts=posts)



#chcp 1251
#PATH C:\Program Files\PostgreSQL\14\bin;%PATH%
#psql -h localhost -p 5432 -d weather_parser -U maxti
#psql -h localhost -p 5432 -d messenger -U maxti

# активировать виртуальную среду
#C:\Users\maxti\PycharmProjects\messenger>venv\Scripts\activate

# запустить flask
# python -m flask run --port 5000

