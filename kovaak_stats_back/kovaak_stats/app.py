import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()

from kovaak_stats.api import api_bp


def create_app(name=__name__, config=False):
    application = Flask(name)
    if not config:
        config = os.environ.get('KOVAAK_STATS_BACK_CONFIG_FILE',
                                sys.prefix + '/www/kovaak_stats_back/app/app.conf')
    if os.path.isfile(config):
        application.config.from_pyfile(config)
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    application.config['SQLALCHEMY_DATABASE_URI'] = application.config.get(
        'SQLALCHEMY_DATABASE_URI',
        'sqlite:///' + sys.prefix + '/www/kovaak_stats_back/app/michel.db'
    )

    from kovaak_stats.utils.login import load_user, request_loader
    login_manager = LoginManager()
    login_manager.init_app(application)
    login_manager.user_loader(load_user)
    login_manager.request_loader(request_loader)

    from kovaak_stats.models.user import User
    db.init_app(application)
    migrate.init_app(application, db)
    application.register_blueprint(api_bp, url_prefix='/api')
    return application
