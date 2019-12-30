from kovaak_stats.app import db
from flask_restplus import Namespace, Resource, fields
from flask_login import login_required
from kovaak_stats.models.user import User
from kovaak_stats.utils.users import user_list


api = Namespace('users', description='Users namespace')

class UserRestResource(Resource):
    """
    Subclass of Resource with the login_required decorator
    """
    method_decorators = [login_required]

user_public_fields = api.model('User', {
    'username': fields.String(description='The username'),
    'email_addr': fields.String(description='The email address'),
})

user_parser = api.parser()
user_parser.add_argument('username', required=True, help='The username')
user_parser.add_argument('email_addr', required=True, help='The email address')
user_parser.add_argument('password', required=True, help='The password')


@api.route('')
class Users(UserRestResource):
    @api.doc(description='Gets the user list')
    @api.response(200, "Everything worked.")
    @api.marshal_list_with(user_public_fields)
    def get(self):
        """
        Gets the user list
        """
        users = user_list()
        return users, 200

    @api.doc(description='Creates a new user')
    @api.expect(user_parser)
    @api.response(200, "Everything worked.")
    @api.response(400, "Bad request")
    @api.marshal_with(user_public_fields)
    def post(self):
        """
        Creates a new user
        """
        args = user_parser.parse_args()
        user = User.create(args.username, args.email_addr, args.password)
        db.session.commit()
        return user, 200


@api.route('/<username>')
class SpecificUser(UserRestResource):
    @api.doc(description='Gets a specific user')
    @api.response(200, "Everything worked.")
    @api.response(404, "The user doesn't exist.")
    @api.marshal_with(user_public_fields)
    def get(self, username):
        """
        Gets a specific user
        """
        user = User.from_db(username)
        if not user:
            api.abort(404, 'No such user')
        return user, 200
