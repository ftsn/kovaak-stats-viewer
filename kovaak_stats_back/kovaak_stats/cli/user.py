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

    parser_right_list = subparser.add_parser(
        'right_list',
        help='Show a user\'s right list',
    )
    parser_right_list.set_defaults(func=users_right_list)
    parser_right_list.add_argument('user', type=check_user, help='The username')

    parser_right_add = subparser.add_parser(
        'right_add',
        help='Add one or multiple rights to user',
    )
    parser_right_add.set_defaults(func=users_right_add)
    parser_right_add.add_argument('user', type=check_user, help='The username')
    parser_right_add.add_argument('rights', nargs='+', help='The rights to add')

    parser_right_del = subparser.add_parser(
        'right_del',
        help='Delete one or multiple rights from user',
    )
    parser_right_del.set_defaults(func=users_right_del)
    parser_right_del.add_argument('user', type=check_user, help='The username')
    parser_right_del.add_argument('rights', nargs='+', help='The rights to delete')


def create_user(username, email_addr, password, **kwargs):
    try:
        User.create(username, email_addr, password)
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    db.session.commit()
    print('User {} created'.format(username))


def users_list(**kwargs):
    users = User.query.all()
    for user in users:
        print(user)


def specific_user_info(user, **kwargs):
    print('Name:', user.name)
    print('Email address:', user.email_addr)
    print('Creation time:', user.creation_date)
    print('Modification time:', user.modification_date)


def specific_user_del(user, **kwargs):
    User.delete(user)
    db.session.commit()
    print('User {} has been deleted'.format(user.name))


def specific_user_modify(user, changes, **kwargs):
    print(changes)
    try:
        user.modify(changes)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    db.session.commit()
    print('User {} has been successfully modified'.format(user.name))


def users_right_list(user, **kwargs):
    for right in user.rights_to_list():
        print(right)


def users_right_add(user, rights, **kwargs):
    for right in rights:
        try:
            user.add_right_from_string(right)
            print('Added the right {} to {}'.format(right, user.name))
        except ValueError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
    db.session.commit()


def users_right_del(user, rights, **kwargs):
    for right in rights:
        try:
            user.del_right_from_string(right)
            print('Deleted the right {} from {}'.format(right, user.name))
        except ValueError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
    db.session.commit()
