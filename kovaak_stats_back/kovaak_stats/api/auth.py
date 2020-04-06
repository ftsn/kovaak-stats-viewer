from flask import redirect, request, current_app, session
from flask_restplus import Resource, Namespace, fields
from requests_oauthlib import OAuth2Session
from kovaak_stats.app import db
from kovaak_stats.models.user import User
from kovaak_stats.utils import Timestamp
from datetime import datetime
import json


api = Namespace('auth', description='Authentication namespace')

redirect_uri = 'http://localhost:9999/api/auth/google-callback'
authorization_base_url = 'https://accounts.google.com/o/oauth2/v2/auth'
token_url = 'https://www.googleapis.com/oauth2/v4/token'
scope = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]


user_public_fields = api.model('User', {
    'name': fields.String(description='The username'),
    'email_addr': fields.String(description='The email address'),
    'rights': fields.List(fields.String, description='The users\' rights'),
    'creation_time': Timestamp(description='The timestamp of the last user modification',
                               attribute='creation_date'),
    'modification_time': Timestamp(description='The timestamp of the last user modification',
                                   attribute='modification_date')
})


@api.route('/google')
class GoogleOauth2(Resource):
    @api.doc(description='Redirect the user to the OAuth provider.')
    def get(self):
        """
        Redirect the user to the OAuth provider
        """
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
        authorization_url, state = google.authorization_url(authorization_base_url,
                                                            access_type="offline", prompt="select_account")
        # State is used to prevent CSRF, keep this for later.
        session['oauth_state'] = state
        return redirect(authorization_url)


@api.route('/google-callback')
class GoogleOauth2Callback(Resource):
    @api.doc(description='Redirect uri given to the provider.')
    @api.marshal_with(user_public_fields, mask='name, email_addr, creation_time, modification_time')
    def get(self):
        """
        Redirect the user to the OAuth provider
        """
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
        google = OAuth2Session(client_id, state=session['oauth_state'], redirect_uri=redirect_uri)
        token = google.fetch_token(token_url, client_secret=client_secret,
                                   authorization_response=request.url)
        session['oauth_token'] = token
        r = google.get('https://www.googleapis.com/oauth2/v1/userinfo')
        content = json.loads(r.content.decode('utf-8'))
        user = User.from_db_by_email(content['email'])
        if not user:
            user = User.create_google(content['email'])
            db.session.commit()

        return user, 204


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
        from kovaak_stats.models.token import Token
        access_token, refresh_token = Token.create_pair(claimed_user)
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
        from kovaak_stats.models.token import Token
        res_access_token = Token.from_db(access_token)
        if res_access_token.is_linked(args.refresh_token) is False:
            api.abort(403, "The access and refresh token aren't paired.")
        refresh_token = Token.from_db(args.refresh_token)
        if refresh_token.has_expired():
            api.abort(403, "The refresh token has expired.")
        res_access_token.refresh()
        refresh_token.delete()
        refresh_token = Token.renew_refresh_token(res_access_token)
        db.session.commit()
        return {"access_token": res_access_token.value, "refresh_token": refresh_token.value}, 200
