from flask import Flask


def create_app(name=__name__):
    application = Flask(name)
    return application