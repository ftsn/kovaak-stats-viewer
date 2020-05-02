import sys
from kovaak_stats.app import db
from kovaak_stats.models.user import User
from kovaak_stats.utils import send_email
from kovaak_stats.utils.users import format_users_stats
from werkzeug.datastructures import FileStorage
from .utils import check_user
from datetime import datetime
import pprint


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

    parser_send_code = subparser.add_parser(
        'send_code',
        help='Send a code to change the password',
    )
    parser_send_code.set_defaults(func=users_send_code)
    parser_send_code.add_argument('user', type=check_user, help='The username')

    parser_get_stats = subparser.add_parser(
        'get_stats',
        help='Show a user\'s stats',
    )
    parser_get_stats.set_defaults(func=users_get_stats)
    parser_get_stats.add_argument('user', type=check_user, help='The username')
    parser_get_stats.add_argument('--scenarii', help='Filter by scenario', nargs='*')
    parser_get_stats.add_argument('--start', type=int,
                                  help='Won\'t return any stats for sessions done before this timestamp',
                                  default=None)
    parser_get_stats.add_argument('--end', type=int,
                                  help='Won\'t return any stats for sessions done after this timestamp',
                                  default=None)

    parser_upload_stats = subparser.add_parser(
        'upload_stats',
        help='Upload stats files',
    )
    parser_upload_stats.set_defaults(func=users_upload_stats)
    parser_upload_stats.add_argument('user', type=check_user, help='The username')
    parser_upload_stats.add_argument('files', help='The files', nargs='+')


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


def users_send_code(user, **kwargs):
    code = user.gen_recovery_code()
    if not code:
        print('A code has already been sent in the last 10 minutes', file=sys.stderr)
        sys.exit(1)
    if send_email('noreply@kovaakstatsviewer.com', user.email_addr,
                  'Recovery code kovaak stats viewer',
                  'The code to change your kovaak stats viewer password is {}'.format(code)) is False:
        user.recovery_code.delete()
        db.session.commit()
        print('Couldn\'t send an email with the code', file=sys.stderr)
        sys.exit(1)
    print('A code has been sent to the email address associated to {}\'s account'.format(user.name))


def users_get_stats(user, scenarii, start, end, **kwargs):
    start = datetime.fromtimestamp(start) if start else datetime.fromtimestamp(0)
    end = datetime.fromtimestamp(end) if end else datetime.fromtimestamp(2147483647)
    from kovaak_stats.models.stat import Stat
    if scenarii:
        stats = Stat.query.filter_by(user_id=user.id).filter(Stat.scenario.in_(scenarii),
                                                             Stat.creation_date >= start,
                                                             Stat.creation_date <= end).order_by(
            Stat.execution_date).all()
    else:
        stats = Stat.query.filter_by(user_id=user.id).filter(Stat.creation_date >= start,
                                                             Stat.creation_date <= end).order_by(
            Stat.execution_date).all()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(format_users_stats(stats))


def users_upload_stats(user, files, **kwargs):
    from kovaak_stats.models.stat import Stat
    for filename in files:
        print('Uploading {}'.format(filename))
        file = FileStorage(stream=open(filename, "rb"), filename=filename, content_type='text/csv')
        try:
            Stat.create(file, user)
        except ValueError as e:
            print('Warning: {}'.format(e), file=sys.stderr)
        except IndexError as e:
            print('Warning: wrong file format'.format(filename), file=sys.stderr)
    db.session.commit()
