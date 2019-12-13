from flask_restplus import Namespace, Resource, fields

api = Namespace('test', description='test namespace')


test_public_fields = api.model('test', {
    'field1': fields.String(description='The field 1'),
    'field2': fields.String(description='The field 2'),
    'field3': fields.String(description='The field 3')
})

test_parser = api.parser()
test_parser.add_argument('toto', required=True, help='toto field')

@api.route('')
class Test(Resource):
    @api.doc(description='This route is solely used to test that everything is setup correctly.')
    @api.expect(test_parser)
    @api.response(200, "Poggers")
    @api.response(400, "Pepehands")
    @api.marshal_with(test_public_fields)
    def get(self):
        """
        Sub documentation
        """
        args = test_parser.parse_args()
        print(args.toto)
        test_obj = {
            'field1': 'tata',
            'field2': 'titi',
            'field3': 'toto'
        }
        return test_obj, 200
