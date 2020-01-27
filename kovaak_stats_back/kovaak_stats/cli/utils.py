import sys
from kovaak_stats.models.user import User


def check_user(username):
    user = User.from_db(username)
    if not user:
        print('User {} doesn\'t exist'.format(username), file=sys.stderr)
        sys.exit(1)
    return user
