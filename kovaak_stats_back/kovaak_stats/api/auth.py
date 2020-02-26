from flask import redirect, request, current_app, session
from flask_restplus import Resource, Namespace
from requests_oauthlib import OAuth2Session
import sys


api = Namespace('auth', description='Authentication namespace')

redirect_uri = 'http://localhost:9999/api/auth/google-callback'
authorization_base_url = 'https://accounts.google.com/o/oauth2/v2/auth'
token_url = 'https://www.googleapis.com/oauth2/v4/token'
scope = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]


@api.route('/google')
class GoogleOauth2(Resource):
    @api.doc(description='Redirect the user to the OAuth provider')
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
class GoogleOauth2(Resource):
    @api.doc(description='Redirect the user to the OAuth provider')
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
        return redirect('http://localhost:8080')
