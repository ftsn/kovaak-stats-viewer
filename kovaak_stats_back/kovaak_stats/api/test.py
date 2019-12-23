from kovaak_stats.app import db
from flask_restplus import Namespace, Resource, fields
from kovaak_stats.models.user import User


api = Namespace('test', description='test namespace')


test_public_fields = api.model('test', {
    'field1': fields.String(description='The field 1'),
    'field2': fields.String(description='The field 2'),
    'field3': fields.String(description='The field 3')
})

test_parser = api.parser()
test_parser.add_argument('username', required=True, help='toto field')

@api.route('')
class Test(Resource):
    @api.doc(description='This route is solely used to test that everything is setup correctly.')
    @api.expect(test_parser)
    @api.response(200, "Poggers")
    @api.response(400, "Pepehands")
    @api.marshal_with(test_public_fields)
    def post(self):
        """
        Sub documentation
        """
        args = test_parser.parse_args()
        test_obj = {
            'field1': 'tata',
            'field2': 'titi',
            'field3': 'toto'
        }
        user = User.create(username=args.username)
        db.session.commit()
        print(user)
        return test_obj, 200
