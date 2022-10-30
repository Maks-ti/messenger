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


    @classmethod
    def insert_returning(cls, query: str) -> object:
        if cls._connection is None:
            cls._connect()
        cls._connection.autocommit = True
        cursor = cls._connection.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchone()
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'the error:\n{ex}')
        else:
            print('the insert returning query is successfully')
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

    def __str__(self):
        string = f'{self.name}:' + '\r\n' + f'{self.login}'
        return string

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
                 image: str = NULL()):
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
        # поле не относящееся к бд
        # необходимо для формирования дерева сообщений (если оно формируется)
        self.child_list = []
        # глубина сообщения в дереве
        self.depth = 0
        # автор сообщения
        self.author: User = Users.get_by_id(self.user_id)


    def tup(self) -> tuple:
        return (self.chat_id,
                self.user_id,
                self.parent_id,
                self.mes_text,
                self.sends_time,)

    def __repr__(self):
        return f'<Message {self.id}>'


class Post(Entity):
    '''
    класс описывает пост
    '''
    def __init__(self,
                 id: int = 0,
                 user_id: int = 0,
                 title: str = '',
                 publication_date: datetime = datetime.now(),
                 last_edit_date: datetime = NULL(),
                 post_text: str = '',
                 image: str = ''):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.publication_date = publication_date
        self.last_edit_date = last_edit_date
        self.post_text = post_text
        self.image = image
        # автор поста User (данные о нём непосредственно в запросе не получаются)
        self.author: User = Users.get_by_id(user_id)
        # коменты опять же получаем отдельно
        self.comments = None


    def tup(self) -> tuple:
        last_edit_date: str
        if self.last_edit_date == NULL():
            last_edit_date = NULL()
        else:
            last_edit_date = str(self.last_edit_date)
        return (self.user_id,
                self.title,
                str(self.publication_date),
                last_edit_date,
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
                 comment_text: str = '',
                 sends_time: datetime = datetime.now()):
        self.id = id
        self.post_id = post_id
        self.commentator_id = commentator_id
        self.comment_text = comment_text
        self.sends_time = sends_time
        # автор коммента
        self.author: User = Users.get_by_id(self.commentator_id)


    def tup(self) -> tuple:
        return (self.post_id,
                self.commentator_id,
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

    @classmethod
    def search_by_text(cls, text: str) -> list[User]:
        ''' поиск пользователей с удовлетворяющим
         именем или логином '''
        query = '''
        SELECT * 
        FROM {}
        WHERE name LIKE '%{}%'
        OR login LIKE '%{}%'
        '''.format(cls.name, text, text)
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return None
        res = list(map(lambda x: User(*x), res))
        return res


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

    @classmethod
    def is_following(cls, follower_id, followed_id) -> bool:
        query = '''
            SELECT * 
            FROM {}
            WHERE {} = {}
            AND {} = {}
            ;
        '''.format(cls.name, cls.columns[0], follower_id, cls.columns[1], followed_id)
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return False
        return True

    @classmethod
    def get_followers(cls, user_id: int) -> list[User]:
        ''' получаем подписчиков user(user_id) '''
        query = '''
            SELECT * 
            FROM {}
            WHERE {} = {}
            ;
        '''.format(cls.name, cls.columns[1], user_id)
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return []
        res = list(map(lambda x: Users.get_by_id(x[0]), res))
        return res

    @classmethod
    def get_followings(cls, user_id: int) -> list[User]:
        ''' получаем подписки user(user_id) '''
        query = '''
            SELECT * 
            FROM {}
            WHERE {} = {}
            ;
        '''.format(cls.name, cls.columns[0], user_id)
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return []
        res = list(map(lambda x: Users.get_by_id(x[1]), res))
        return res


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
    def add(cls, chat: Chat) -> int:
        query = '''
        INSERT INTO {}
        ( {} )
        VALUES
        {}
        RETURNING id
        ;
        '''.format(cls.name, ', '.join(cls.columns), chat.tup())
        res = _DataBase.insert_returning(query)
        if res is None or len(res) == 0:
            return None
        return res[0]


    @classmethod
    def delete(cls, id: int) -> bool:
        query = cls._delete_query.format(cls.name, id)
        return _DataBase.execute_query(query)

    @classmethod
    def get_chats_with_2_users(cls, current_user_id: int, other_user_id: int) -> list[Chat]:
        '''поиск общих чатов для двух пользователей'''
        query = '''
        SELECT id, name, counter, image 
        FROM user_in_chat AS usch INNER JOIN user_in_chat AS usch2
        ON usch.chat_id = usch2.chat_id AND usch.user_id = {} AND usch2.user_id = {}
        INNER JOIN chat ON usch.chat_id = chat.id
        '''.format(current_user_id, other_user_id)
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return None
        res = list(map(lambda x: Chat(*x), res))
        return res

    @classmethod
    def get_chat_by_id(cls, chat_id: int) -> Chat:
        query = '''
        SELECT * 
        FROM {}
        WHERE id = {}
        '''.format(cls.name, chat_id)
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return None
        res = res[0]
        return Chat(*res)


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

    @classmethod
    def is_user_in_chat(cls, chat_id: int, user_id: int) -> bool:
        query = '''
        SELECT * 
        FROM {}
        WHERE chat_id = {} 
        AND user_id = {}
        '''.format(cls.name, chat_id, user_id)
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return False
        return True

    @classmethod
    def get_users_chats(cls, user_id: int) -> list[Chat]:
        query = '''
        SELECT DISTINCT {}
        FROM user_in_chat JOIN chat 
        ON user_in_chat.chat_id = chat.id
        WHERE user_in_chat.user_id = {}
        '''.format('id, '+', '.join(Chats.columns), user_id)
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return None
        res = list(map(lambda x: Chat(*x), res))
        return res


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

    @classmethod
    def get_messages_by_chat_id(cls, chat_id) -> list[Message]:
        query = '''
        SELECT *
        FROM {}
        WHERE chat_id = {}
        ORDER BY sends_time
        '''.format(cls.name, chat_id)
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return None
        res = list(map(lambda x: Message(*x), res))
        return res


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
        ORDER BY {} DESC
        '''.format(cls.name, user_id, cls.columns[2])
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return None
        res = list(map(lambda x: Post(*x), res))
        return res

    @classmethod
    def get_followed_posts(cls, user_id: int) -> list[Post]:
        '''SELECT post_params
            FROM post join follows
            ON user_id = followed_id
            WHERE follower_id = current_user_id
            order by publication_date DESC'''
        query = '''
        SELECT {}
        FROM {} INNER JOIN {} 
        ON {} = {}
        WHERE {} = {}
        ORDER BY {} DESC
        '''.format('id, ' + ', '.join(cls.columns),
                   cls.name,
                   Follows.name,
                   cls.columns[0],
                   Follows.columns[1],
                   Follows.columns[0],
                   user_id,
                   cls.columns[2])
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return None
        res = list(map(lambda x: Post(*x), res))
        return res

    @classmethod
    def get_all_posts(cls) -> list[Post]:
        query = '''
        SELECT *
        FROM {}
        ORDER BY {} DESC
        '''.format(cls.name, cls.columns[2])
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return None
        res = list(map(lambda x: Post(*x), res))
        return res

    @classmethod
    def get_post_by_id(cls, id: int) -> Post:
        query = '''
        SELECT * 
        FROM {}
        WHERE id = {}
        '''.format(cls.name, id)
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return None
        res = res[0]
        return Post(*res)

    @classmethod
    def update(cls, post) -> bool:
        query = '''
        UPDATE {}
        SET 
        title = '{}' ,
        post_text = '{}' ,
        last_edit_date = '{}'
        WHERE id = {}
        '''.format(cls.name,
                   post.title,
                   post.post_text,
                   str(post.last_edit_date),
                   post.id)
        return _DataBase.execute_query(query)

    @classmethod
    def search_by_text(cls, text: str) -> list[Post]:
        ''' поиск всех постов с удовлетворяющим заголовком '''
        query = '''
        SELECT *
        FROM {}
        WHERE title LIKE '%{}%'
        '''.format(cls.name, text)
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

    @classmethod
    def get_comments_by_post_id(cls, post_id: int):
        query = '''
        SELECT *
        FROM {}
        WHERE post_id = {}
        '''.format(cls.name, post_id)
        res = _DataBase.select_query(query)
        if res is None or len(res) == 0:
            return None
        res = list(map(lambda x: Comment(*x), res))
        return res



# метод загрузки пользователя (не трогать)
@login.user_loader
def load_user(id: str):
    user: User = Users.get_by_id(int(id))
    print(f'user loaded; user = {user}')
    return user

