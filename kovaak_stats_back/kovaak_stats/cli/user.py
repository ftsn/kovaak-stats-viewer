import sys
from kovaak_stats.app import db
from kovaak_stats.models.user import User
from .utils import check_user


def subparser_install(subparser):
    parser_user_create = subparser.add_parser(
        'create',
        help='Create a user',
    )
    parser_user_create.set_defaults(func=create_user)
    parser_user_create.add_argument('username', help='The username')
    parser_user_create.add_argument('email_addr', help='The user\'s email address')
    parser_user_create.add_argument('password', help='The user\'s password')

    parser_user_list = subparser.add_parser(
        'list',
        help='List the users',
    )
    parser_user_list.set_defaults(func=users_list)

    parser_specific_user_show = subparser.add_parser(
        'show',
        help='Show the information of a specific user',
    )
    parser_specific_user_show.set_defaults(func=specific_user_info)
    parser_specific_user_show.add_argument('user', type=check_user,
                                           help='The user whose information should be retrieved')

    parser_specific_user_del = subparser.add_parser(
        'del',
        help='Delete a specific user',
    )
    parser_specific_user_del.set_defaults(func=specific_user_del)
    parser_specific_user_del.add_argument('user', type=check_user, help='The user who should be deleted')

    parser_specific_user_modify = subparser.add_parser(
        'modify',
        help='Modify a specific user',
    )
    parser_specific_user_modify.set_defaults(func=specific_user_modify)
    parser_specific_user_modify.add_argument('user', type=check_user, help='The user who should be modified')
    parser_specific_user_modify.add_argument('changes', help='Set of changes to be applied to the resource')


def create_user(username, email_addr, password, **kwargs):
    try:
        User.create(username, email_addr, password)
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    db.session.commit()
    print('User {} created'.format(username))


def users_list(**kwargs):
    print(User.query.all())


def specific_user_info(user, **kwargs):
    print('Name:', user.name)
    print('Email address:', user.email_addr)
    print('Creation time:', user.creation_date)
    print('Modification time:', user.modification_date)


def specific_user_del(user, **kwargs):
    User.delete(user)
    db.session.commit()
    print('User {) has been deleted'.format(user.name))


def specific_user_modify(user, changes, **kwargs):
    print(changes)
    try:
        user.modify(changes)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    db.session.commit()
    print('User {} has been successfully modified'.format(user.name))
