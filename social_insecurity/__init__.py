"""Provides the social_insecurity package for the Social Insecurity application.

The package contains the Flask application factory.
"""

from pathlib import Path
from shutil import rmtree
from typing import cast

from flask import Flask, current_app, Response

from social_insecurity.config import Config
from social_insecurity.database import SQLite3

# from flask_login import LoginManager
from flask_bcrypt import Bcrypt 
from flask_wtf.csrf import CSRFProtect

sqlite = SQLite3()
bcrypt = Bcrypt()
# TODO: Handle login management better, maybe with flask_login?
# login = LoginManager()
# TODO: The CSRF protection is not working, I should probably fix that
csrf = CSRFProtect()


def create_app(test_config=None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.from_object(test_config)

    sqlite.init_app(app, schema="schema.sql")
    bcrypt.init_app(app)
    # login.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        create_uploads_folder(app)

    @app.cli.command("reset")
    def reset_command() -> None:
        """Reset the app."""
        instance_path = Path(current_app.instance_path)
        if instance_path.exists():
            rmtree(instance_path)

    @app.after_request
    def add_security_headers(response: Response) -> Response:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net https://maxcdn.bootstrapcdn.com; "
            "style-src 'self' https://cdn.jsdelivr.net https://maxcdn.bootstrapcdn.com 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self'; "
            "frame-src 'none';"
            "frame-ancestors 'self'; "   # Restrict embedding to same origin
            "form-action 'self'; "       # Restrict form submissions to same origin
        )
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'  # Prevents clickjacking
        return response
    with app.app_context():
        import social_insecurity.routes  # noqa: E402,F401

    return app


def create_uploads_folder(app: Flask) -> None:
    """Create the instance and upload folders."""
    upload_path = Path(app.instance_path) / cast(str, app.config["UPLOADS_FOLDER_PATH"])
    if not upload_path.exists():
        upload_path.mkdir(parents=True)
