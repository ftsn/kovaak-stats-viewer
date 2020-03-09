from kovaak_stats.app import db
from flask_restplus import Namespace, Resource, fields
from flask_login import login_required
from kovaak_stats.models.right import Right
from kovaak_stats.utils import right_needed, Timestamp


api = Namespace('rights', description='Rights namespace')


class RightRestResource(Resource):
    """
    Subclass of Resource with the login_required decorator
    """
    method_decorators = [login_required]


rights_public_fields = api.model('Right', {
    'name': fields.String(description='The name of the right'),
    'creation_time': Timestamp(description='The timestamp of the last user modification',
                               attribute='creation_date'),
    'modification_time': Timestamp(description='The timestamp of the last user modification',
                                   attribute='modification_date')
})


right_parser = api.parser()
right_parser.add_argument('rights', required=True, help='The rights\' names', action='append')


@api.route('')
class Users(RightRestResource):
    @api.header('Authorization', 'Basic or Bearer', required=True)
    @api.doc(description='Get the right list')
    @api.response(200, "Everything worked.")
    @api.marshal_list_with(rights_public_fields)
    @right_needed('rights.get')
    def get(self):
        """
        Get the right list
        """
        return Right.query.all(), 200

    @api.header('Authorization', 'Basic or Bearer', required=True)
    @api.doc(description='Create a new right')
    @api.expect(right_parser)
    @api.response(200, "Everything worked.")
    @api.response(400, "Bad request")
    @api.marshal_with(rights_public_fields)
    @right_needed('rights.create')
    def post(self):
        """
        Create new rights
        """
        args = right_parser.parse_args()
        try:
            for right_name in args.rights:
                right = Right.create(right_name)
        except ValueError as e:
            api.abort(400, e)
        db.session.commit()
        return right, 200


@api.route('/<right_name>')
class SpecificUser(RightRestResource):
    @api.header('Authorization', 'Basic or Bearer', required=True)
    @api.doc(description='Gets a specific right')
    @api.response(200, "Everything worked.")
    @api.response(404, "The right doesn't exist.")
    @api.marshal_with(rights_public_fields)
    @right_needed('rights.get')
    def get(self, right_name):
        """
        Get a specific right
        """
        right = Right.from_db(right_name)
        if not right:
            api.abort(404, 'No such right')
        return right, 200

    @api.doc(description='Delete a specific right')
    @api.response(204, "Everything worked.")
    @api.response(404, "The right doesn't exist.")
    @right_needed('rights.del')
    def delete(self, right_name):
        """
        Delete a specific right
        """
        right = Right.from_db(right_name)
        if not right:
            api.abort(404, 'No such right')
        right.delete()
        db.session.commit()
        return '', 204
