# Description: This file contains the configuration settings for the application.

import os
from datetime import timedelta
from dotenv import load_dotenv
from main.extensions import db

load_dotenv()

class Config:
    # configuration go here
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = "sqlalchemy"
    SESSION_SQLALCHEMY = db
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    