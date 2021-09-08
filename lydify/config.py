# Python
from flask import Flask
from os import environ

from .constants import LYDIFY_MODE_ENV

class Config(object):
    DEBUG = False
    TESTING = False
    SPOTIFY_CLIENT_ID = environ.get("SPOTIFY_CLIENT_ID")
    SPOTIFY_SECRET = environ.get("SPOTIFY_SECRET")
    ENV = environ.get(LYDIFY_MODE_ENV)

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG=True


def init_config(app: Flask):
    mode = environ.get(LYDIFY_MODE_ENV)
    if mode == "development":
        app.config.from_object(DevelopmentConfig)
    elif mode == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(Config)
