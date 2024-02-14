""" The main module for the Flask application. """
from flask import Flask
from flask_cors import CORS

from backend.app.config import configs
from backend.app.routes.auth_blueprint import auth_blueprint
from backend.app.routes.main_blueprint import main_blueprint


def create_app(config_name='dev'):
    """
    Create and configure the Flask application.

    Args:
        config_name (str): The name of the configuration to use.
        Possible values are 'dev', 'test', or 'prod'.

    Returns:
        Flask: The configured Flask application.
    """
    app = Flask(__name__)

    config = configs[config_name]

    app.config.from_object(config)

    CORS(app, supports_credentials=True, origins=app.config['CORS_ORIGINS'])

    # Import and register blueprints
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(main_blueprint, url_prefix='/')

    return app
