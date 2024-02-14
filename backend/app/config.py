"""This module contains the configuration classes for the application."""

import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


class Config:
    """
    Configuration class for the application.

    Attributes:
        BASE_URL (str): The base URL of the application.
        TOKEN_DIR (str): The directory path for storing tokens.
        API_CREDS_PATH (str): The path to the API credentials file.
        CORS_ORIGINS (list): The list of allowed origins for CORS.
        SECRET_KEY (str): The secret key for JWT authentication.
        SESSION_COOKIE_SAMESITE (str): The SameSite attribute for session cookies.
        SESSION_COOKIE_SECURE (bool): Whether to use secure session cookies.
        SESSION_COOKIE_HTTPONLY (bool): Whether to use HTTP-only session cookies.
        PERMANENT_SESSION_LIFETIME (timedelta): The lifetime of permanent sessions.
        SESSION_COOKIE_PARTITIONED (bool): Whether to partition session cookies.
    """
    BASE_URL = 'https://sync-calendar-app-xt6u7vzbeq-de.a.run.app'
    TOKEN_DIR = '/tokens'
    API_CREDS_PATH = '/secrets/api_credentials.json'
    CORS_ORIGINS = ['https://moodle.ncku.edu.tw',
                    'https://sync-calendar-app-xt6u7vzbeq-de.a.run.app']

    SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_PARTITIONED = True


class DevelopmentConfig(Config):
    """
    Configuration class for development environment.
    Inherits from the base Config class.
    """
    DEBUG = True
    API_CREDS_PATH = './secrets/api_credentials.json'
    BASE_URL = 'http://localhost:8080'
    TOKEN_DIR = '.'


class TestingConfig(Config):
    """
    Configuration class for testing environment.
    Inherits from the base Config class.
    """
    TESTING = True
    API_CREDS_PATH = './secrets/api_credentials.json'
    BASE_URL = 'http://localhost:8080'
    TOKEN_DIR = '.'


class ProductionConfig(Config):
    """
    Configuration class for production environment.
    Inherits from the base Config class.
    """
    DEBUG = False


configs = {
    "dev": DevelopmentConfig,
    "test": TestingConfig,
    "prod": ProductionConfig
}
