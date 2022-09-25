from flask import Flask
from flask_login import LoginManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
# задаём функцию просмотра[для входа] (необходимо для использования @login_required)
login.login_view = 'login'

from app import routes, models, errors
