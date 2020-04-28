from flask import current_app
from flask_restplus import Resource, Namespace, fields
from kovaak_stats.app import db
from kovaak_stats.models.user import User
from kovaak_stats.utils import Timestamp
from datetime import datetime
from oauth2client import client
from kovaak_stats.models.token import Token as TokenModel
import json
import requests


api = Namespace('auth', description='Authentication namespace')

redirect_uri = 'http://localhost:9999/api/auth/google-callback'
authorization_base_url = 'https://accounts.google.com/o/oauth2/v2/auth'
token_url = 'https://www.googleapis.com/oauth2/v4/token'
scope = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]
fetch_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'


user_public_fields = api.model('User', {
    'name': fields.String(description='The username'),
    'email_addr': fields.String(description='The email address'),
    'rights': fields.List(fields.String, description='The users\' rights'),
    'creation_time': Timestamp(description='The timestamp of the last user modification',
                               attribute='creation_date'),
    'modification_time': Timestamp(description='The timestamp of the last user modification',
                                   attribute='modification_date')
})


google_user_public_fields = api.model('GoogleUser', {
    'name': fields.String(description='The username'),
    'access_token': fields.String(description='The access token'),
    'rights': fields.List(fields.String, description='The users\' rights'),
})


google_tokens_parser = api.parser()
google_tokens_parser.add_argument('auth', required=True, help='The auth code')


@api.route('/google-tokens')
class GoogleOauth2Tokens(Resource):
    @api.doc(description='Fetch a pair of google tokens and create, if needed, the corresponding new user in db')
    @api.response(200, "Everything worked.")
    @api.response(400, "Can't get the tokens")
    @api.marshal_with(google_user_public_fields)
    def post(self):
        """
        Get a google token pair
        """
        args = google_tokens_parser.parse_args()
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
        auth_code = args.auth
        try:
            credentials = client.credentials_from_code(client_id, client_secret, scope='', code=auth_code)
        except client.FlowExchangeError as e:
            api.abort(400, e)

        r = requests.get('{}?access_token={}'.format(fetch_info_url, credentials.access_token))
        content = json.loads(r.content.decode('utf-8'))
        user = User.from_db_by_email(content['email'])
        if not user:
            try:
                user = User.create_google(content['email'])
            except ValueError as e:
                api.abort(400, 'Cannot create the user. More information: {}'.format(e))
        TokenModel.create_pair(user,
                               raw_access={
                                   'type': 'access-google',
                                   'value': credentials.access_token,
                                   'expiration_date': credentials.token_expiry
                               },
                               raw_refresh={
                                   'type': 'refresh-google',
                                   'value': credentials.refresh_token
                               })
        db.session.commit()
        return {'name': user.name, 'access_token': credentials.access_token, 'rights': user.rights}, 200


token_create_parser = api.parser()
token_create_parser.add_argument('username', required=True, help='The username')
token_create_parser.add_argument('password', required=True, help='The password')


@api.route('/token-pair')
class TokenPair(Resource):
    @api.doc(description='Get a JWT / refresh token pair')
    @api.expect(token_create_parser)
    @api.response(401, "Invalid username/password.")
    @api.response(403, "The user already has an access token. Refresh the token instead.")
    @api.response(200, "Everything worked.")
    def post(self):
        """
        Get a JWT / refresh token pair
        """
        args = token_create_parser.parse_args()
        claimed_user = User.from_db_basic(args.username, args.password)
        if not claimed_user:
            api.abort(401, "Invalid username/password.")
        #if claimed_user.tokens:
        #    if claimed_user.tokens[1].has_expired() is False:
        #        api.abort(403, "{} already has an access token. Refresh the token instead.".format(args.username))
        access_token, refresh_token = TokenModel.create_pair(claimed_user)
        db.session.commit()
        tokens = {
            "access_token": {
                "value": access_token.value
            },
            "refresh_token": {
                "value": refresh_token.value,
                "expiration_time": datetime.timestamp(refresh_token.expiration_date)
            }
        }
        return tokens, 200


token_refresh_parser = api.parser()
token_refresh_parser.add_argument('refresh_token', required=True, help='The refresh token')


@api.route('/<access_token>/refresh')
class Token(Resource):
    @api.doc(description='Refresh a user\'s JWT and issues a new refresh token at the same time')
    @api.expect(token_refresh_parser)
    @api.response(403, "The access and refresh token aren't paired.")
    @api.response(403, "The refresh token has expired.")
    @api.response(200, "Everything worked.")
    def post(self, access_token):
        """
        Refresh a JWT and get a new refresh token
        """
        args = token_refresh_parser.parse_args()
        res_access_token = TokenModel.from_db(access_token)
        if res_access_token.is_linked(args.refresh_token) is False:
            api.abort(403, "The access and refresh token aren't paired.")
        refresh_token = TokenModel.from_db(args.refresh_token)
        if refresh_token.has_expired():
            api.abort(403, "The refresh token has expired.")
        res_access_token.refresh()
        refresh_token.delete()
        refresh_token = TokenModel.renew_refresh_token(res_access_token)
        db.session.commit()
        return {"access_token": res_access_token.value, "refresh_token": refresh_token.value}, 200
