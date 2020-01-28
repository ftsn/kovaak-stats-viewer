import sys
from kovaak_stats.app import db
from kovaak_stats.models.right import Right
from .utils import check_right


def subparser_install(subparser):
    parser_right_create = subparser.add_parser(
        'create',
        help='Create a right',
    )
    parser_right_create.set_defaults(func=create_right)
    parser_right_create.add_argument('name', help='The right\'s name')

    parser_right_list = subparser.add_parser(
        'list',
        help='List the rights',
    )
    parser_right_list.set_defaults(func=rights_list)

    parser_specific_right_show = subparser.add_parser(
        'show',
        help='Show the information of a specific right',
    )
    parser_specific_right_show.set_defaults(func=specific_right_info)
    parser_specific_right_show.add_argument('right', type=check_right,
                                            help='The user of which information should be retrieved')

    parser_specific_right_del = subparser.add_parser(
        'del',
        help='Delete a specific right',
    )
    parser_specific_right_del.set_defaults(func=specific_right_del)
    parser_specific_right_del.add_argument('right', type=check_right, help='The right which should be deleted')


def create_right(name, **kwargs):
    try:
        Right.create(name)
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    db.session.commit()
    print('Right {} created'.format(name))


def rights_list(**kwargs):
    rights = Right.query.all()
    for right in rights:
        print(right)


def specific_right_info(right, **kwargs):
    print('Name:', right.name)
    print('Creation time:', right.creation_date)


def specific_right_del(right, **kwargs):
    Right.delete(right)
    db.session.commit()
    print('Right {) has been deleted'.format(right.name))

