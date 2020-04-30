from functools import wraps
from flask import g, current_app
from flask_restplus import abort, fields
from flask_login import current_user
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def get_current_user():
    if hasattr(g, 'current_user') and g.current_user:
        return g.current_user
    return current_user._get_current_object()


def right_needed(rightname):
    def wrap(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            from kovaak_stats.models.right import Right
            right = Right.from_db(rightname)
            if not right:
                abort(403, '{} right doesn\'t exist'.format(rightname))
            if right not in get_current_user().rights:
                abort(403, 'You don\'t have the right {} required to do the request'.format(rightname))
            return f(*args, **kwargs)
        return wrapped
    return wrap


class Timestamp(fields.Raw):
    def format(self, value):
        return datetime.timestamp(value)


def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH')
    return response


def send_email(from_addr, to_addr, subject, content):
    if current_app.config.get('RECOVER_SEND_MAIL') == 'false':
        return True
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    try:
        server.login(current_app.config.get('GOOGLE_USERNAME'), current_app.config.get('GOOGLE_PASSWORD'))
    except AttributeError:
        return False

    msg = MIMEMultipart()
    msg['From'] = 'noreply@kovaakstatsviewer.com'
    msg['To'] = to_addr
    msg['Subject'] = subject

    msg.attach(MIMEText(content, 'plain'))
    text = msg.as_string()
    server.sendmail(from_addr, to_addr, text)

    server.quit()
    return True
