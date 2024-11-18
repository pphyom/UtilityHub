# Description: This file contains the configuration settings for the application.

import os, secrets
from datetime import timedelta
from dotenv import load_dotenv
from main.extensions import db

load_dotenv()

class Config:
    # configuration go here
    SECRET_KEY = secrets.token_urlsafe(16)
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = "sqlalchemy"
    SESSION_SQLALCHEMY_TABLE = "live_sessions"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    SESSION_SQLALCHEMY = db
    