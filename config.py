# Description: This file contains the configuration settings for the application.

import os, secrets
from dotenv import load_dotenv
from main.extensions import db

load_dotenv()

class Config:
    # configuration go here
    SECRET_KEY = secrets.token_urlsafe(16)
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = "sqlalchemy"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_SQLALCHEMY = db
    FIRMWARE_FOLDER = os.getenv("FIRMWARE_FOLDER")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

    # Create the firmware folder if not exists. Use it to store firmware files.
    os.makedirs(FIRMWARE_FOLDER, exist_ok=True)