'''
файл моделей(таблиц) базы данных и классов для взаимодействия с ней
'''

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

from abc import ABC, abstractmethod
import psycopg2
from datetime import datetime


class NULL(object):
    '''
    класс NULL, реализует патерн singleton
    лечит null значение для postgress
    (синглтон не обязателен но так проще)
    '''
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(NULL, cls).__new__(cls)
        return cls.instance

    def __repr__(self):
        return 'null'


class _DataBase(object):
    '''
    класс описывающий базу даннных
    данный клас будет инкапсулировать в себе все необходимые для подключения к базе
    параметры (при разработке они будут захардкочены, как их прокинуть будет придумано позже)
    будет реализован метод возвращающий connection - объект соединения с базой,
    который как раз таки будет необходим в методах класса Table и его потоммков
    '''
    _db_name = 'messenger'
    _db_user = 'maxti'
    _user_password = '1Alexandr1'
    _db_host = 'localhost'
    _db_port = '5432'

    _connection: psycopg2 = None

    @classmethod
    def _connect(cls) -> psycopg2:
        try:
            cls._connection = psycopg2.connect(
                database=cls._db_name,
                user=cls._db_user,
                password=cls._user_password,
                host=cls._db_host,
                port=cls._db_port,
            )
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'other error:\n{ex}')
        else:
            print("connection to PostgreSQL DB successful")
        return cls._connection


    # insert / update / delete
    @classmethod
    def execute_query(cls, query: str) -> bool:
        if cls._connection is None:
            cls._connect()
        cls._connection.autocommit = True
        cursor = cls._connection.cursor()
        try:
            cursor.execute(query)
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'the error:\n{ex}')
        else:
            print('the query executed successfully')
            return True
        return False


    # select
    @classmethod
    def select_query(cls, query: str) -> list:
        if cls._connection is None:
            cls._connect()
        cls._connection.autocommit = True
        cursor = cls._connection.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchall()
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'the error:\n{ex}')
        else:
            print('the select query is successfully')
            return result
        return None


''' //---//---//---// ENTITIES //---//---//---// '''
class Entity(ABC):
    @abstractmethod
    def tup(self) -> tuple:
        '''
        метод возвращает кортеж для добавления его в базуданных
        предполагается, что если в скрипте создания таблицы
        поле id генерирутеся автоматически, возвращать данное значение
        не нужно, в противном случае наоборот необходимо'''
        pass


class User(UserMixin, Entity):
    '''
    класс пользователя
    описывает пользователя как класс
    '''
    def __init__(self,
                 id: int = 0,
                 login: str = '',
                 password_hash: str = '',
                 name: str = ''):
        self.id: int = id
        self.login: str = login
        self.name: str = name
        self.password_hash: str = password_hash


    def __repr__(self):
        return f'<User {self.login}>'


    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)


    def tup(self) -> tuple:
        return (self.login,
                self.password_hash,
                self.name,)


class Profile(Entity):
    '''
    класс описывающий профиль пользователя
    '''
    def __init__(self,
                 id: int,
                 profile_img: str = NULL(),
                 biography: str = '',
                 about: str = ''):
        self.id = id
        self.profile_img = profile_img
        self.biography = biography
        self.about = about

    def tup(self) -> tuple:
        return (self.id,
                self.profile_img,
                self.biography,
                self.about,)

    def __eq__(self, other):
        if other is None:
            return True
        return False

    def avatar(self) -> str:
        print(self.profile_img)
        if self.profile_img == '' or self.profile_img == NULL() or self.profile_img is None:
            return None
        return self.profile_img


class Chat(Entity):
    '''
    класс описывающий сущность чата
    '''
    def __init__(self,
                 id: int = 0,
                 name: str = '',
                 counter: int = 0,
                 image: object = NULL()):
        self.id = id
        self.name = name
        self.counter = counter
        self.image = image

    def tup(self) -> tuple:
        return (self.name,
                self.counter,
                self.image,)


class Message(Entity):
    '''
    класс описывающий сообщение
    '''
    def __init__(self,
                 id: int = 0,
                 chat_id: int = 0,
                 user_id: int = 0,
                 parent_id: int = NULL(),
                 mes_text: str = '',
                 sends_time: datetime = datetime.now()):
        self.id = id
        self.chat_id = chat_id
        self.user_id = user_id
        self.parent_id = parent_id
        self.mes_text = mes_text
        self.sends_time = sends_time

    def tup(self) -> tuple:
        return (self.chat_id,
                self.user_id,
                self.parent_id,
                self.mes_text,
                self.sends_time,)


class Post(Entity):
    '''
    класс описывает пост
    '''
    def __init__(self,
                 id: int = 0,
                 user_id: int = 0,
                 title: str = '',
                 publication_date: datetime = datetime.now(),
                 last_edit_date: datetime = datetime.now(),
                 post_text: str = '',
                 image: object = NULL()):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.publication_date = publication_date
        self.last_edit_date = last_edit_date
        self.post_text = post_text
        self.image = image
        # автор поста User не храниться в базе (однако является очень удобной связкой для представления поста в шаблонах)
        self.author: User = Users.get_by_id(user_id)

    def tup(self) -> tuple:
        return (self.user_id,
                self.title,
                str(self.publication_date),
                str(self.last_edit_date),
                self.post_text,
                self.image,)

    def __repr__(self):
        return f'<Post {self.title}>'


class Comment(Entity):
    '''
    класс описывающий коментарий кпосту
    '''
    def __init__(self,
                 id: int = 0,
                 post_id: int = 0,
                 commentator_id: int = 0,
                 parent_id: int = NULL(),
                 comment_text: str = '',
                 sends_time: datetime = datetime.now()):
        self.id = id
        self.post_id = post_id
        self.commentator_id = commentator_id
        self.parent_id = parent_id
        self.comment_text = comment_text
        self.sends_time = sends_time

    def tup(self) -> tuple:
        return (self.post_id,
                self.commentator_id,
                self.parent_id,
                self.comment_text,
                str(self.sends_time),)


''' //---//---//---// TABLES //---//---//---// '''
class Table(ABC):
    '''
    класс описывающий сущность/таблицу в базе
    является абстрактным
    и содержит минимальный набор методов, необходимый для реализации:
    это методы
    - add - добавления записи о сущности в базу
    - get - получения обекта сущности, в соответсвии с идентификатором (и значениями из базы)
    '''
    name = 'table'
    columns: list[str]
    # insert_query.format('table_name', 'columns...', values: tuple)
    _insert_query = '''
    INSERT INTO {}
    ( {} )
    VALUES
    {}
    ;
    '''

    _delete_query = '''
    DELETE
    FROM {}
    WHERE id = {}
    ;
    '''

    @classmethod
    @abstractmethod
    def add(cls, obj: object) -> bool:
        pass

    @classmethod
    @abstractmethod
    def delete(cls, *params) -> bool:
        pass


class Users(Table):
    '''
    класс описывает таблицу, хранящую информацию о пользователях
    '''

    name = 'users'
    columns = [
        'login',
        'password_hash',
        'name',
    ]
    _get_by_id_query = '''
        SELECT *
        FROM {}
        WHERE id = {}
        ;
        '''

    @classmethod
    def add(cls, user: User) -> bool:
        query = cls._insert_query.format(cls.name, ', '.join(cls.columns), user.tup())
        return _DataBase.execute_query(query)

    @classmethod
    def get_by_id(cls, id: int) -> User:
        query = cls._get_by_id_query.format(cls.name, id)
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return None
        params = res[0]
        return User(* params)

    @classmethod
    def get_by_login(cls, login: str) -> User:
        query = '''
        SELECT * 
        FROM {}
        WHERE login = '{}'
        ;
        '''.format(cls.name, login)
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return None
        params = res[0]
        return User(* params)

    @classmethod
    def delete(cls, id: int) -> bool:
        query = cls._delete_query.format(cls.name, id)
        return _DataBase.execute_query(query)

    @classmethod
    def update_name(cls, user_id: int, name: str) -> bool:
        query = '''
        UPDATE {}
        SET name = '{}'
        WHERE id = {}
        ;'''.format(cls.name, name, user_id)
        return _DataBase.execute_query(query)


class Profiles(Table):
    '''
    класс описывающий таблицу профилей пользователя
    связана один-к-одному с таблицей users
    '''

    name = 'profile_info'
    columns = [
        'id',
        'profile_img',
        'biography',
        'about',
    ]
    @classmethod
    def add(cls, profile: Profile) -> bool:
        query = cls._insert_query.format(cls.name, ', '.join(cls.columns), profile.tup())
        return _DataBase.execute_query(query)

    @classmethod
    def delete(cls, id: int) -> bool:
        query = cls._delete_query.format(cls.name, id)
        return _DataBase.execute_query(query)

    @classmethod
    def get_by_id(cls, id: int) -> Profile:
        query = '''
        SELECT * 
        FROM {}
        WHERE id = {};
        '''.format(cls.name, id)
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return None
        res = res[0]
        return Profile(* res)

    @classmethod
    def update(cls, new_profile: Profile) -> bool:
        profile = Profiles.get_by_id(new_profile.id)
        query: str
        if profile is None:
            query = cls._insert_query.format(cls.name, ', '.join(cls.columns), new_profile.tup())
        else:
            query = '''
            UPDATE {}
            SET profile_img = '{}',
            biography = '{}',
            about = '{}'
            WHERE id = {}
            '''.format(cls.name,
                       new_profile.profile_img,
                       new_profile.biography,
                       new_profile.about,
                       new_profile.id)
        return _DataBase.execute_query(query)


class Follows(Table):
    '''
    класс описывает таблицу
    реализующую связь многие-ко-многим для
    таблиц users и users (связь сама с собой)
    '''

    name = 'follows'
    columns = ['follower_id', 'followed_id']

    @classmethod
    def add(cls, follower_id: int, followed_id: int) -> bool:
        query = cls._insert_query.format(cls.name, ', '.join(cls.columns), (follower_id, followed_id))
        return _DataBase.execute_query(query)

    @classmethod
    def delete(cls, follower_id: int, followed_id: int) -> bool:
        query = '''
            DELETE
            FROM {}
            WHERE {} = {}
            AND {} = {}
            ;
        '''.format(cls.name, cls.columns[0], follower_id, cls.columns[1], followed_id)
        return _DataBase.execute_query(query)


class Chats(Table):
    '''
    класс описыает таблицу чатов
    '''

    name = 'chat'
    columns = [
        'name',
        'counter',
        'image',
    ]

    @classmethod
    def add(cls, chat: Chat) -> bool:
        query = cls._insert_query.format(cls.name, ', '.join(cls.columns), chat.tup())
        return _DataBase.execute_query(query)

    @classmethod
    def delete(cls, id: int) -> bool:
        query = cls._delete_query.format(cls.name, id)
        return _DataBase.execute_query(query)


class User_in_chat(Table):
    '''
    класс реализует связь многие-ко-многим для
    таблиц users и chat
    '''

    name = 'user_in_chat'
    columns = ['user_id', 'chat_id']

    @classmethod
    def add(cls, user_id: int, chat_id: int) -> bool:
        query = cls._insert_query.format(cls.name, ', '.join(cls.columns), (user_id, chat_id))
        return _DataBase.execute_query(query)

    @classmethod
    def delete(cls, user_id: int, chat_id: int) -> bool:
        query = '''
            DELETE
            FROM {}
            WHERE {} = {}
            AND {} = {}
            ;
        '''.format(cls.name, cls.columns[0], user_id, cls.columns[1], chat_id)
        return _DataBase.execute_query(query)


class Messages(Table):
    '''
    класс описывающий талицу сообщений
    '''

    name = 'message'
    columns = [
        'chat_id',
        'user_id',
        'parent_id',
        'mes_text',
        'sends_time',
    ]

    @classmethod
    def add(cls, message: Message) -> bool:
        query = cls._insert_query.format(cls.name, ', '.join(cls.columns), message.tup())
        return _DataBase.execute_query(query)

    @classmethod
    def delete(cls, id: int) -> bool:
        query = cls._delete_query.format(cls.name, id)
        return _DataBase.execute_query(query)


class Posts(Table):
    '''
    класс описывающий таблицу постов
    '''

    name = 'post'
    columns = [
        'user_id',
        'title',
        'publication_date',
        'last_edit_date',
        'post_text',
        'image',
    ]

    @classmethod
    def add(cls, post: Post) -> bool:
        query = cls._insert_query.format(cls.name, ', '.join(cls.columns), post.tup())
        return _DataBase.execute_query(query)

    @classmethod
    def delete(cls, id: int) -> bool:
        query = cls._delete_query.format(cls.name, id)
        return _DataBase.execute_query(query)

    @classmethod
    def get_posts_by_user_id(cls, user_id: int) -> list[Post]:
        query = '''
        SELECT *
        FROM {}
        WHERE user_id = {}
        '''.format(cls.name, user_id)
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return None
        res = list(map(lambda x: Post(*x), res))
        return res


class Comments(Table):
    '''
    класс описывающий комментарий к посту
    '''

    name = 'comment'
    columns = [
        'post_id',
        'commentator_id',
        'parent_id',
        'comment_text',
        'sends_time',
    ]

    @classmethod
    def add(cls, comment: Comment) -> bool:
        query = cls._insert_query.format(cls.name, ', '.join(cls.columns), comment.tup())
        return _DataBase.execute_query(query)

    @classmethod
    def delete(cls, id: int) -> bool:
        query = cls._delete_query.format(cls.name, id)
        return _DataBase.execute_query(query)



# метод загрузки пользователя (не трогать)
@login.user_loader
def load_user(id: str):
    user: User = Users.get_by_id(int(id))
    print(f'user loaded; user = {user}')
    return user

