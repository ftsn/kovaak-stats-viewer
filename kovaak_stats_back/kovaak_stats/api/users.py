from kovaak_stats.app import db
from flask_restplus import Namespace, Resource, fields
from flask_login import login_required
from kovaak_stats.models.user import User
from jsonpointer import JsonPointerException
from kovaak_stats.utils import right_needed, Timestamp
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
    @api.marshal_list_with(user_public_fields, mask='name, email_addr, creation_time, modification_time')
    @right_needed('users.get')
    def get(self):
        """
        Get the user list
        """
        return User.query.all(), 200

    @api.doc(description='Create a new user')
    @api.expect(user_create_parser)
    @api.response(200, "Everything worked.")
    @api.response(400, "Bad request")
    @api.marshal_with(user_public_fields)
    @right_needed('users.create')
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


right_add_parser = api.parser()
right_add_parser.add_argument('name', required=True, help='The right\'s name')

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
    @api.marshal_with(users_rights_public_fields)
    @right_needed('users.rights_add')
    def post(self, username):
        """
        Add a right to a user
        """
        args = right_add_parser.parse_args()
        user = User.from_db(username)
        if not user:
            api.abort(404, 'No such user')
        from kovaak_stats.models.right import Right
        if not Right.exists(args.name):
            api.abort(404, 'No such right')
        if user.has_right(args.name):
            api.abort(400, 'The user already has this right')
        user.add_right_from_string(args.name)
        db.session.commit()

        return user, 200


@api.route('/<username>/rights/<right_name>')
class UserSpecificRight(UserRestResource):
    @api.doc(description='Delete a right from a user')
    @api.response(204, "Everything worked.")
    @api.response(400, "The user doesn't have this right.")
    @api.response(404, "No such right")
    @api.response(404, "No such user")
    @api.marshal_with(users_rights_public_fields)
    @right_needed('users.rights_delete')
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
        if not user.has_right(right_name):
            api.abort(400, 'The user doesn\'t have this right')
        user.del_right_from_string(right_name)
        db.session.commit()

        return user, 200
