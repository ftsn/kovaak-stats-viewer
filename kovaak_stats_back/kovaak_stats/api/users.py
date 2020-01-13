from kovaak_stats.app import db
from flask_restplus import Namespace, Resource, fields
from flask_login import login_required
from kovaak_stats.models.user import User


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
})

user_parser = api.parser()
user_parser.add_argument('username', required=True, help='The username')
user_parser.add_argument('email_addr', required=True, help='The email address')
user_parser.add_argument('password', required=True, help='The password')


@api.route('')
class Users(UserRestResource):
    @api.doc(description='Get the user list')
    @api.response(200, "Everything worked.")
    @api.marshal_list_with(user_public_fields)
    def get(self):
        """
        Get the user list
        """
        return User.query.all(), 200

    @api.doc(description='Create a new user')
    @api.expect(user_parser)
    @api.response(200, "Everything worked.")
    @api.response(400, "Bad request")
    @api.marshal_with(user_public_fields)
    def post(self):
        """
        Create a new user
        """
        args = user_parser.parse_args()
        user = User.create(args.username, args.email_addr, args.password)
        db.session.commit()
        return user, 200


@api.route('/<username>')
class SpecificUser(UserRestResource):
    @api.doc(description='Get a specific user')
    @api.response(200, "Everything worked.")
    @api.response(404, "The user doesn't exist.")
    @api.marshal_with(user_public_fields)
    def get(self, username):
        """
        Get a specific user
        """
        user = User.from_db(username)
        if not user:
            api.abort(404, 'No such user')
        return user, 200


right_public_fields = api.model('Right', {
    'name': fields.String(description='The right\'s name'),
})


right_add_parser = api.parser()
right_add_parser.add_argument('name', required=True, help='The right\'s name')



@api.route('/<username>/rights')
class UserRight(UserRestResource):
    @api.doc(description='Get a user\'s rights')
    @api.response(200, "Everything worked.")
    @api.response(404, "The user doesn't exist.")
    def get(self, username):
        """
        Get a user's rights
        """
        user = User.from_db(username)
        if not user:
            api.abort(404, 'No such user')
        return user.rights, 200

    @api.doc(description='Add a right to a user')
    @api.expect(right_add_parser)
    @api.response(200, "Everything worked.")
    @api.response(400, "Bad request")
    @api.response(400, "The user already has this right.")
    @api.response(400, "No such right")
    @api.response(404, "No such user")
    @api.marshal_with(user_public_fields)
    def post(self, username):
        args = right_add_parser.parse_args()

        user = User.from_db(username)
        if not user:
            api.abort(404, 'No such user')
        from kovaak_stats.models.right import Right
        right = Right.query.filter_by(name=args.name).first()
        if right is None:
            api.abort(400, 'No such right')
        if right in user.rights:
            api.abort(400, 'The user already has this right')

        user.rights.append(right)
        db.session.commit()

        return user, 200

@api.route('/<username>/rights/<right_name>')
class UserSpecificRight(UserRestResource):
    @api.doc(description='Delete a right from a user')
    @api.response(204, "Everything worked.")
    @api.response(400, "The user doesn't have this right.")
    @api.response(404, "No such right")
    @api.response(404, "No such user")
    @api.marshal_with(user_public_fields)
    def delete(self, username, right_name):
        user = User.from_db(username)
        if not user:
            api.abort(404, 'No such user')
        from kovaak_stats.models.right import Right
        right = Right.query.filter_by(name=right_name).first()
        if right is None:
            api.abort(404, 'No such right')
        if right not in user.rights:
            api.abort(400, 'The user doesn\'t have this right')

        user.rights.remove(right)
        db.session.commit()

        return user, 204
