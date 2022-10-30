'''
файл конфигурации приложения
'''

import os

'''
класс конфигурации приложения
'''
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-my-key'
    UPLOAD_FOLDER = 'C:/Users/maxti/PycharmProjects/messenger/app/static/images/'
    DB_NAME = 'messenger'
    DB_USER = 'maxti'
    USER_PASSWORD = 'psql_password'
    DB_HOST = 'localhost'
    DB_PORT = '5432'
