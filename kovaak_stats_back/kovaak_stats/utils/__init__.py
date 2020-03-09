from functools import wraps
from flask import g
from flask_restplus import abort, fields
from flask_login import current_user
from datetime import datetime


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
