from kovaak_stats.models.user import User, AuthenticationError
from flask import abort


def load_user(user_id):
    return User.from_db(user_id)


def request_loader(request):
    auth = request.headers.get('Authorization')

    if not auth:
        return None

    method, token = auth.split(' ')
    try:
        if method == 'Basic':
            return User.from_basic_auth(token)
        else:
            abort(400)
    except AuthenticationError:
        abort(401)

    return None
