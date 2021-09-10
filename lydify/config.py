# Python
from flask import Flask
from os import getenv

from .constants import LYDIFY_MODE_ENV, ConfigType
from .utils import get_authorization

from dataclasses import dataclass


@dataclass
class YoutubeConfig:
    type: str = ConfigType.YOUTUBE


@dataclass
class SpotifyConfig:
    type: str = ConfigType.SPOTIFY
    redirect_uri: str = getenv("REDIRECT_URI", "http://localhost:5000/callback")
    client_id: str = getenv("SPOTIFY_CLIENT_ID")
    client_secret: str = getenv("SPOTIFY_CLIENT_SECRET")
    authorization: str = get_authorization(ConfigType.SPOTIFY)


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "secret-key"
    ENV = getenv(LYDIFY_MODE_ENV)
    SPOTIFY = SpotifyConfig()
    YOUTUBE = YoutubeConfig()


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True


def init_config(app: Flask):
    mode = getenv(LYDIFY_MODE_ENV)
    if mode == "development":
        app.config.from_object(DevelopmentConfig)
    elif mode == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(Config)
