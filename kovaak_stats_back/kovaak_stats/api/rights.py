from kovaak_stats.app import db
from flask_restplus import Namespace, Resource, fields
from flask_login import login_required
from kovaak_stats.models.right import Right


api = Namespace('rights', description='Rights namespace')


class RightRestResource(Resource):
    """
    Subclass of Resource with the login_required decorator
    """
    method_decorators = [login_required]


right_public_fields = api.model('Right', {
    'name': fields.String(description='The right\'s name'),
})

right_parser = api.parser()
right_parser.add_argument('name', required=True, help='The right\'s name')


@api.route('')
class Users(RightRestResource):
    @api.doc(description='Get the right list')
    @api.response(200, "Everything worked.")
    @api.marshal_list_with(right_public_fields)
    def get(self):
        """
        Get the right list
        """
        return Right.query.all(), 200

    @api.doc(description='Create a new right')
    @api.expect(right_parser)
    @api.response(200, "Everything worked.")
    @api.response(400, "Bad request")
    @api.marshal_with(right_public_fields)
    def post(self):
        """
        Create a new right
        """
        args = right_parser.parse_args()
        right = Right.create(args.name)
        db.session.commit()
        return right, 200


@api.route('/<right>')
class SpecificUser(RightRestResource):
    @api.doc(description='Gets a specific right')
    @api.response(200, "Everything worked.")
    @api.response(404, "The right doesn't exist.")
    @api.marshal_with(right_public_fields)
    def get(self, right):
        """
        Get a specific right
        """
        right = Right.from_db(right)
        if not right:
            api.abort(404, 'No such right')
        return right, 200
