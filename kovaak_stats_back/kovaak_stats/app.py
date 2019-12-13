import os
import sys
from flask import Flask
from kovaak_stats.api import api_bp


def create_app(name=__name__, config=False):
    application = Flask(name)
    if not config:
        config = os.environ.get('KOVAAK_STATS_BACK_CONFIG_FILE',
                                sys.prefix + '/www/console.bocal.org/app/app.conf')
    if os.path.isfile(config):
        application.config.from_pyfile(config)
    application.register_blueprint(api_bp, url_prefix='/api')
    return application
