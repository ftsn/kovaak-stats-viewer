import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from kovaak_stats.api import api_bp


db = SQLAlchemy()
migrate = Migrate()

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

    db.init_app(application)
    migrate.init_app(application, db)
    application.register_blueprint(api_bp, url_prefix='/api')
    return application
