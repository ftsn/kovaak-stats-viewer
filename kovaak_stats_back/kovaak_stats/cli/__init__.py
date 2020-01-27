from argparse import ArgumentParser
from kovaak_stats.app import create_app
from .user import subparser_install as user_subparser

MAIN_COMMANDS = [
    ('user', user_subparser),
]


def main():
    """
    Main entry point
    """

    parser = ArgumentParser()
    app = create_app()

    subparser = parser.add_subparsers(dest='main_command', help='The main command')
    subparser.required = True

    for command in MAIN_COMMANDS:
        cmd_parser = subparser.add_parser(command[0])
        cmd_subparser = cmd_parser.add_subparsers(dest='sub_command', help='The {0} sub-command'.format(command[0]))
        cmd_subparser.required = True
        command[1](cmd_subparser)

    with app.app_context():
        args = parser.parse_args()

        args.cls = args.main_command
        args.func(**vars(args))
