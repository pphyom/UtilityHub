
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_login import LoginManager
from flask_socketio import SocketIO


db = SQLAlchemy()

sess = Session()

login_manager = LoginManager()

socketio = SocketIO()
