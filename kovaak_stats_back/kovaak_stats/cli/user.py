import sys
from kovaak_stats.app import db
from kovaak_stats.models.user import User


def subparser_install(subparser):
    parser_user_create = subparser.add_parser(
        'create',
        help='Create A User',
    )
    parser_user_create.set_defaults(func=create_user)
    parser_user_create.add_argument('username', help='The user\'s firstname')
    parser_user_create.add_argument('email_addr', help='The user\'s email address')
    parser_user_create.add_argument('password', help='The user\'s password')

    parser_user_list = subparser.add_parser(
        'list',
        help='List users for a domain',
    )
    parser_user_list.set_defaults(func=users_list)


def create_user(username, email_addr, password, **kwargs):
    try:
        user = User.create(username, email_addr, password)
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    db.session.commit()
    print('User {} created'.format(user))


def users_list(**kargs):
    print(User.query.all())
