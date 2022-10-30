'''
файл конфигурации приложения
'''

import os

'''
класс конфигурации приложения
'''
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-my-key'
    UPLOAD_FOLDER = '../static/images/'
    DB_NAME = 'db7cidiio5adqm'
    DB_USER = 'bnxarcjxwfflya'
    USER_PASSWORD = 'a59a9cf68c5b7185da43dbffb132ebe7ce4ae58bf65cf46e4b43a235df7baa86'
    DB_HOST = 'ec2-52-23-131-232.compute-1.amazonaws.com'
    DB_PORT = '5432'
