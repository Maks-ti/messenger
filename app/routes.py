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
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, MessageForm, CommentForm, SearchForm, ChatForm
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
    posts = Posts.get_followed_posts(current_user.id)
    if posts is None:
        posts = []
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


@app.route('/user/<login>', methods=['GET', 'POST'])
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
    # если мы на своей странице
    if login == current_user.login:
        # мадюем форму написания поста
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
            return redirect(url_for('user', login=login))
        return render_template('user.html', form=form, user=user, posts=posts, profile=profile, Follows=Follows, len=len)
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
        if profile is None:
            profile = Profile(id=current_user.id)
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
        if profile is not None:
            form.name.data = current_user.name
            form.about.data = profile.about
            form.biography.data = profile.biography
        else:
            form.name.data = current_user.name
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


@app.route('/explore', methods=['GET', 'POST'])
@app.route('/explore/<keyword>', methods=['GET', 'POST'])
@login_required
def explore(keyword=None):
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('explore', keyword=form.text.data))
    posts: list[Post]
    users: list[User] = None
    if keyword is None:
        posts = Posts.get_all_posts()
    else:
        posts = Posts.search_by_text(keyword)
        if posts is None:
            posts = []
        users = Users.search_by_text(keyword)
    return render_template('explore.html', form=form, posts=posts, users=users)


@app.route('/edit_post/<post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Posts.get_post_by_id(post_id)
    if post is None:
        abort(404)
    # если юзер попытался вбить url и исправить чужой пост
    if post.author.id != current_user.id:
        abort(404)
    # если всё ок, то заполним форму тем что было и отрисуем страницу
    form = PostForm()
    if form.validate_on_submit():
        post = Post(id=post_id,
                    user_id=current_user.id,
                    title=form.title.data,
                    post_text=form.post_text.data,
                    publication_date=post.publication_date,
                    last_edit_date=datetime.now())
        file = form.image.data
        # если файл добавлен, то обновим и его тоже
        if file is not None and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            post.image = '../static/images/' + filename
        Posts.update(post)
        flash('Your post updated')
        return redirect(url_for('user', login=current_user.login))
    elif request.method == 'GET':
        form.title.data = post.title
        form.post_text.data = post.post_text
    return render_template('edit_post.html', title='Edit post', form=form)


@app.route('/comment/<post_id>', methods=['GET', 'POST'])
@login_required
def comment(post_id):
    post = Posts.get_post_by_id(post_id)
    if post is None:
        abort(404)
    post.comments = Comments.get_comments_by_post_id(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        # формируем коммент
        comment = Comment(0,
                          post_id,
                          current_user.id,
                          form.text.data,
                          datetime.now())
        Comments.add(comment)
        return redirect(url_for('comment', post_id=post_id))
    return render_template('comment.html', form=form, post=post, answer_id=post_id)


@app.route('/write/<login>')
@login_required
def write(login):
    ''' метод занимается перенаправлением юзера в нужный чат
     при необходимости чат создаётся и юзеры в него добавляется '''
    user: User = Users.get_by_login(login)
    if user is None:
        flash('User {} not found.'.format(login))
        return redirect(url_for('index'))
    if user.id == current_user.id:
        flash('You can`t write to yourself')
        return redirect(url_for('index'))
    chats = Chats.get_chats_with_2_users(current_user.id, user.id)
    print(chats)
    if chats is None:
        # создаём новый чат и перенаправляем юзера туда
        chat_name = current_user.name + " and " + user.name
        chat = Chat(name=chat_name)
        # создаём чат и получаем его id
        chat_id = Chats.add(chat)
        # если есть проблемы создания (проблемы базы) вызовем ошибку
        if chat_id is None:
            abort(500)
        # добавляем юзеров в созданный чат
        User_in_chat.add(current_user.id, chat_id)
        User_in_chat.add(user.id, chat_id)
    else:
        # берём первый чат и перенаправляем юзера туда
        chat = chats[0]
        chat_id = chat.id
    return redirect(url_for('chat', chat_id=chat_id, parent_id=None))


@app.route('/chat/<chat_id>', methods=['GET', 'POST'])
@app.route('/chat/<chat_id>/<parent_id>', methods=['GET', 'POST'])
@login_required
def chat(chat_id, parent_id=None):
    if parent_id is not None:
        parent_id = int(parent_id)
    chat = Chats.get_chat_by_id(chat_id)
    # если чат е сущестует
    if chat is None:
        abort(404)
    # если юзера нет в этом чате
    if not User_in_chat.is_user_in_chat(chat_id, current_user.id):
        abort(404)
    # форма ввода
    form = MessageForm()
    if form.validate_on_submit():
        # формируем сообщение
        message = Message(chat_id=chat_id,
                          user_id=current_user.id,
                          mes_text=form.text.data,
                          sends_time=str(datetime.now()))
        if parent_id is not None:
            message.parent_id = parent_id
        Messages.add(message)
        return redirect(url_for('chat', chat_id=chat_id, parent_id=None))
    # получаем дерево сообщений
    messages = Messages.get_messages_by_chat_id(chat_id)
    if messages is None:
        messages = []
    else:
        messages = create_tree(messages)
    return render_template('chat.html', title='chat', chat=chat, form=form, messages=messages, parent_id=parent_id)


def create_tree(all_messages: list[Message]) -> list:
    # сдоварь для упорядочивания записей (каждому parent_id соответствует список дочерних сообщений)
    sorter = dict()
    for mes in all_messages:
        if mes.parent_id not in sorter:
            sorter[mes.parent_id] = []
        sorter[mes.parent_id].append(mes)
    # формирование дерева (теперь преобразуем словарь в дерево из списокв)
    res = sorter[None]
    form_list(res, sorter, 0)
    return res


def form_list(lst: list[Message], sorter: dict, depth: int):
    for mes in lst:
        if mes.id in sorter:
            mes.child_list = sorter[mes.id]
        mes.depth = depth
        form_list(mes.child_list, sorter, depth+1)


@app.route('/chats', methods=['GET', 'POST'])
@login_required
def chats():
    chats: list[Chat] = User_in_chat.get_users_chats(current_user.id)
    if chats is None:
        chats = []
    form = ChatForm()
    # устанавливаем список юзеров которых можно добавиь в чт (добавить можно тех на кого ты подписан)
    choices = Follows.get_followings(current_user.id)
    if choices is None:
        choices = []
    form.users.choices = [(u.id, f'{u.name}:' + '\r\n' + f'{u.login}') for u in choices]
    if form.validate_on_submit():
        print(form.users.data)
        chat = Chat(name=form.chat_name.data)
        chat_id = Chats.add(chat)
        # если есть проблемы создания
        if chat_id is None:
            abort(500)
        # добавляем выбранных юзеров в чат
        for u_id in form.users.data:
            User_in_chat.add(u_id, chat_id)
        # себя тоже добавляем
        User_in_chat.add(current_user.id, chat_id)
        return redirect(url_for('chat', chat_id=chat_id))
    return render_template('chats.html', chats=chats, form=form)




#chcp 1251
#PATH C:\Program Files\PostgreSQL\14\bin;%PATH%
#psql -h localhost -p 5432 -d weather_parser -U maxti
#psql -h localhost -p 5432 -d messenger -U maxti

# активировать виртуальную среду
#C:\Users\maxti\PycharmProjects\messenger>venv\Scripts\activate

# запустить flask
# python -m flask run --port 5000
