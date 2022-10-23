# -*- coding: utf-8 -*-
'''
файл функций просмотра (файл представлений)
'''
import os
from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app import app
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
# наверноепроще просто заимпортить все модели предваритеьно установив моификаторы доступа rpotected на те которые импортить не надо (или определить функцию импорта)
from app.models import User, Profile, Chat, Message, Post, Comment
from app.models import Users, Profiles, Follows, Chats, User_in_chat, Messages, Posts, Comments



@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    '''
    условно домашняя страница
    с лентой новостей (из постов юзеров на которых
    текущий юзер подписан
    '''
    form = PostForm()
    if form.validate_on_submit():
        post = Post(user_id=current_user.id,
                    title=form.title.data,
                    post_text=form.post_text.data,
                    publication_date=datetime.now())
        file = form.image.data
        # если файл добавлен, то обновим и его тоже
        if file is not None and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            post.image = '../static/images/' + filename
        Posts.add(post)
        flash('Your post added')
        return redirect(url_for('index'))
    posts = Posts.get_followed_posts(current_user.id)
    return render_template('index.html', form=form, title='Home', posts=posts)


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
    posts: list[Post] = Posts.get_posts_by_user_id(user.id)
    if posts is None:
        posts = []
    profile: Profile = Profiles.get_by_id(user.id)
    if profile is None:
        profile = Profile(user.id)
    return render_template('user.html', user=user, posts=posts, profile=profile, Follows=Follows, len=len)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    # если внесены изменения (метод post) проверяем вадидаторы
    if form.validate_on_submit():
        name = form.name.data
        about = form.about.data
        biography = form.biography.data
        profile = Profiles.get_by_id(current_user.id)
        profile.about = about
        profile.biography = biography
        file = form.image.data
        # если файл добавлен, то обновим и его тоже
        if file is not None and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            profile.profile_img = '../static/images/' + filename
        # обновляем данные
        Profiles.update(profile)
        Users.update_name(current_user.id, name)
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    # если только вызвали страницу заполняем поля старыми (существующими сейчас) значениями
    elif request.method == 'GET':
        profile = Profiles.get_by_id(current_user.id)
        form.name.data = current_user.name
        form.about.data = profile.about
        form.biography.data = profile.biography
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<login>')
@login_required
def follow(login):
    user: User = Users.get_by_login(login)
    if user is None:
        flash('User {} not found.'.format(login))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', login=login))
    # добавляем подписку на User`а
    Follows.add(current_user.id, user.id)
    flash('You are following {} !'.format(login))
    return redirect(url_for('user', login=login))


@app.route('/unfollow/<login>')
@login_required
def unfollow(login):
    user: User = Users.get_by_login(login)
    if user is None:
        flash('User {} not found.'.format(login))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', login=login))
    Follows.delete(current_user.id, user.id)
    flash('You are not following {}.'.format(login))
    return redirect(url_for('user', login=login))


@app.route('/followers/<login>')
@login_required
def followers(login):
    user: User = Users.get_by_login(login)
    if user is None:
        return redirect(url_for('index'))
    followers = Follows.get_followers(user.id)
    return render_template('followers.html', followers=followers)


@app.route('/followings/<login>')
@login_required
def followings(login):
    user: User = Users.get_by_login(login)
    if user is None:
        return redirect(url_for('index'))
    followings = Follows.get_followings(user.id)
    return render_template('followings.html', followings=followings)



#chcp 1251
#PATH C:\Program Files\PostgreSQL\14\bin;%PATH%
#psql -h localhost -p 5432 -d weather_parser -U maxti
#psql -h localhost -p 5432 -d messenger -U maxti

# активировать виртуальную среду
#C:\Users\maxti\PycharmProjects\messenger>venv\Scripts\activate

# запустить flask
# python -m flask run --port 5000

