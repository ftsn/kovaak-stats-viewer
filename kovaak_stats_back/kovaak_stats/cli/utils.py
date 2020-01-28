import sys
from kovaak_stats.models.user import User
from kovaak_stats.models.right import Right


def check_user(username):
    user = User.from_db(username)
    if not user:
        print('User {} doesn\'t exist'.format(username), file=sys.stderr)
        sys.exit(1)
    return user


def check_right(name):
    right = Right.from_db(name)
    if not right:
        print('Right {} doesn\'t exist'.format(name), file=sys.stderr)
        sys.exit(1)
    return right
