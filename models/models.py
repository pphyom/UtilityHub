import json
from sqlalchemy import TypeDecorator, String
from flask_login import UserMixin
from main.extensions import db


class JSONType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect=None):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialet=None):
        if value is not None:
            return json.loads(value)
        return value


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


class Firmware(db.Model):
    __tablename__ = "firmware"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Firmware {self.filename}>"

class Commands(db.Model):
    __tablename__ = "commands"

    id = db.Column(db.Integer, primary_key=True)
    tool = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    cmd = db.Column(JSONType, nullable=False)

    def __repr__(self):
        return f"<Commands {self.name}>"