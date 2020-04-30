from kovaak_stats.app import db
from flask_restplus import Namespace, Resource, fields
from flask_login import login_required
from kovaak_stats.models.user import User
from kovaak_stats.utils import get_current_user
from kovaak_stats.utils.users import hash_pw
from jsonpointer import JsonPointerException
from kovaak_stats.utils import right_needed, Timestamp, send_email
from kovaak_stats.utils.users import format_users_stats
from werkzeug.datastructures import FileStorage
from datetime import datetime
import json
import jsonpatch


api = Namespace('users', description='Users namespace')


class UserRestResource(Resource):
    """
    Subclass of Resource with the login_required decorator
    """
    method_decorators = [login_required]


user_public_fields = api.model('User', {
    'name': fields.String(description='The username'),
    'email_addr': fields.String(description='The email address'),
    'rights': fields.List(fields.String, description='The users\' rights'),
    'creation_time': Timestamp(description='The timestamp of the last user modification',
                               attribute='creation_date'),
    'modification_time': Timestamp(description='The timestamp of the last user modification',
                                   attribute='modification_date')
})

user_create_parser = api.parser()
user_create_parser.add_argument('username', required=True, help='The username')
user_create_parser.add_argument('email_addr', required=True, help='The email address')
user_create_parser.add_argument('password', required=True, help='The password')


@api.route('')
class Users(UserRestResource):
    @api.doc(description='Get the user list')
    @api.response(200, "Everything worked.")
    @api.marshal_list_with(user_public_fields)
    @right_needed('users.get')
    def get(self):
        """
        Get the user list
        """
        return User.query.all(), 200


@api.route('')
class UsersCreate(Resource):
    @api.doc(description='Create a new user')
    @api.expect(user_create_parser)
    @api.response(200, "Everything worked.")
    @api.response(400, "Bad request")
    @api.marshal_with(user_public_fields)
    def post(self):
        """
        Create a new user
        """
        args = user_create_parser.parse_args()
        try:
            user = User.create(args.username, args.email_addr, args.password)
        except ValueError as e:
            api.abort(400, 'Cannot create the user. More information: {}'.format(e))
        db.session.commit()
        return user, 200


user_modify_parser = api.parser()
user_modify_parser.add_argument('changes', required=True, help='Set of changes to be applied to the resource')


@api.route('/<username>')
class SpecificUser(UserRestResource):
    @api.doc(description='Get a specific user')
    @api.response(200, "Everything worked.")
    @api.response(404, "The user doesn't exist.")
    @api.marshal_with(user_public_fields)
    @right_needed('users.get')
    def get(self, username):
        """
        Get a specific user
        """
        user = User.from_db(username)
        if not user:
            api.abort(404, 'No such user')
        return user, 200

    @api.doc(description='Modify a specific user')
    @api.expect(user_modify_parser)
    @api.response(200, "Everything worked.")
    @api.response(404, "The user doesn't exist.")
    @api.marshal_with(user_public_fields)
    @right_needed('users.modify')
    def patch(self, username):
        """
        Modify a specific user
        """
        user = User.from_db(username)
        if not user:
            api.abort(404, 'No such user')
        args = user_modify_parser.parse_args()

        try:
            user.modify(args.changes)
        except json.decoder.JSONDecodeError:
            api.abort(400, "Badly formatted JSON")
        except TypeError:
            api.abort(400, "A JSON list following the JSON patch format is expected")
        except (jsonpatch.InvalidJsonPatch, JsonPointerException) as e:
            api.abort(400, "Invalid JSON patch format. More information: {}".format(e))
        except jsonpatch.JsonPatchConflict as e:
            api.abort(409, "Conflict in the set of changes. More information: {}".format(e))
        except ValueError as e:
            api.abort(400, "Invalid value(s) in the set of changes. More information: {}".format(e))

        db.session.commit()
        return user, 200

    @api.doc(description='Delete a specific user')
    @api.response(204, "Everything worked.")
    @api.response(404, "The user doesn't exist.")
    @right_needed('users.del')
    def delete(self, username):
        """
        Delete a specific user
        """
        user = User.from_db(username)
        if not user:
            api.abort(404, 'No such user')
        user.delete()
        db.session.commit()
        return '', 204


right_add_parser = api.parser()
right_add_parser.add_argument('rights', required=True, help='The rights\' names', action='append')

users_rights_public_fields = api.model('UsersRights', {
    'rights': fields.List(fields.String, attribute='rights'),
})


@api.route('/<username>/rights')
class UserRight(UserRestResource):
    @api.doc(description='Get a user\'s rights')
    @api.response(200, "Everything worked.")
    @api.response(404, "The user doesn't exist.")
    @api.marshal_with(users_rights_public_fields)
    @right_needed('users.rights_get')
    def get(self, username):
        """
        Get a user's rights
        """
        user = User.from_db(username)
        if not user:
            api.abort(404, 'No such user')
        return user, 200

    @api.doc(description='Add a right to a user')
    @api.expect(right_add_parser)
    @api.response(200, "Everything worked.")
    @api.response(400, "Bad request")
    @api.response(400, "The user already has this right.")
    @api.response(400, "No such right")
    @api.response(404, "No such user")
    @right_needed('users.rights_add')
    def post(self, username):
        """
        Add one or multiple rights to a user
        """
        args = right_add_parser.parse_args()
        user = User.from_db(username)
        if not user:
            api.abort(404, 'No such user')
        try:
            for right_name in args.rights:
                user.add_right_from_string(right_name)
        except ValueError as e:
            api.abort(400, e)
        db.session.commit()

        return '', 204


@api.route('/<username>/rights/<right_name>')
class UserSpecificRight(UserRestResource):
    @api.doc(description='Delete a right from a user')
    @api.response(204, "Everything worked.")
    @api.response(400, "The user doesn't have this right.")
    @api.response(404, "No such right")
    @api.response(404, "No such user")
    @right_needed('users.rights_del')
    def delete(self, username, right_name):
        """
        Delete a right from a user
        """
        user = User.from_db(username)
        if not user:
            api.abort(404, 'No such user')
        from kovaak_stats.models.right import Right
        if not Right.exists(right_name):
            api.abort(404, 'No such right')
        try:
            user.del_right_from_string(right_name)
        except ValueError as e:
            api.abort(400, e)
        db.session.commit()

        return '', 204


recovery_public_fields = api.model('RecoveryCode', {
    'code': fields.String,
})

password_recovery_parser = api.parser()
password_recovery_parser.add_argument('recovery_code', required=True, help='The recovery code')
password_recovery_parser.add_argument('new_password', required=True, help='The new password')


@api.route('/<username>/recover')
class UserPasswordRecover(Resource):
    @api.doc(description='Generate a recovery code a user who wants to change his password')
    @api.response(200, "Everything worked.")
    @api.response(404, "No such user")
    @api.marshal_with(recovery_public_fields)
    def get(self, username):
        user = User.from_db(username)
        if not user:
            api.abort(404, 'No such user')
        code = user.gen_recovery_code()
        if not code:
            api.abort(409, 'A code has already been sent in the last 10 minutes')
        if send_email('noreply@kovaakstatsviewer.com', 'zarobrya@hotmail.fr',
                      'Recovery code kovaak stats viewer',
                      'The code to change your kovaak stats viewer password is {}'.format(code)) is False:
            user.recovery_code.delete()
            db.session.commit()
            api.abort(400, 'Couldn\'t send an email with the code')
        return '', 204

    @api.doc(description='Change the password of the user if the recovery code is correct')
    @api.expect(password_recovery_parser)
    @api.response(204, "Everything worked.")
    @api.response(403, "The recovery code is incorrect or has expired")
    @api.response(404, "No such user")
    @api.marshal_with(user_public_fields)
    def post(self, username):
        args = password_recovery_parser.parse_args()
        user = User.from_db(username)
        if not user:
            api.abort(404, 'No such user')
        from kovaak_stats.models.recovery_code import RecoveryCode
        provided_code = RecoveryCode.from_db(args.recovery_code, user.id)
        if not provided_code or provided_code.has_expired():
            api.abort(403, "The recovery code is incorrect or has expired")
        user.hashed_pw = hash_pw(args.new_password).decode('utf-8')
        db.session.commit()
        return '', 204


upload_parser = api.parser()
upload_parser.add_argument('files', location='files', type=FileStorage, required=True, action='append')

get_stats_parser = api.parser()
get_stats_parser.add_argument('scenarii', help='Will only return the stats for these scenarii', action='append')
get_stats_parser.add_argument('start', help='Won\'t return any stats for sessions done before this timestamp')
get_stats_parser.add_argument('end', help='Won\'t return any stats for sessions done after this timestamp')


@api.route('/<username>/stats')
class UserStats(Resource):
    @api.doc(description='Return the stats associated to a certain user')
    @api.expect(get_stats_parser)
    @api.response(200, "Everything worked.")
    @api.response(404, "No such user")
    def get(self, username):
        args = get_stats_parser.parse_args()
        user = User.from_db(username)
        if not user:
            api.abort(404, 'No such user')
        if not get_current_user().has_right('stats.get') and get_current_user().name != username:
            api.abort(403, 'You don\'t have the proper right or try to access the stats of someone else')
        try:
            start = datetime.fromtimestamp(int(args.start)) if args.start else datetime.fromtimestamp(0)
            end = datetime.fromtimestamp(int(args.end)) if args.end else datetime.fromtimestamp(2147483647)
        except TypeError:
            api.abort(400, "Invalid value, a timestamp is expected")
        from kovaak_stats.models.stat import Stat
        if args.scenarii:
            stats = Stat.query.filter_by(user_id=user.id).filter(Stat.scenario.in_(args.scenarii),
                                                                 Stat.creation_date >= start,
                                                                 Stat.creation_date <= end).order_by(Stat.execution_date).all()
        else:
            stats = Stat.query.filter_by(user_id=user.id).filter(Stat.creation_date >= start,
                                                                 Stat.creation_date <= end).order_by(Stat.execution_date).all()
        return format_users_stats(stats), 200

    @api.doc(description='Parse the stats from the files sent with the request and add them to a corresponding user')
    @api.expect(upload_parser)
    @api.response(204, "Everything worked.")
    @api.response(400, "Error while processing a stat file")
    @api.response(404, "No such user")
    def post(self, username):
        args = upload_parser.parse_args()
        user = User.from_db(username)
        if not user:
            api.abort(404, 'No such user')
        from kovaak_stats.models.stat import Stat
        for file in args.files:
            try:
                Stat.create(file, user)
            except ValueError as e:
                api.abort(400, e)
        db.session.commit()
        return '', 204
