from tests import TestCaseApi
from kovaak_stats.app import db
from kovaak_stats.models.user import User
import datetime

AUTH_URL = '/api/auth'


class TestApiAuth(TestCaseApi):
    def test_auth_create_token_pair_wrong_credentials(self):
        """Test to create a token pair when providing wrong credentials"""
        status, data = self.post('{}/{}'.format(AUTH_URL, 'token-pair'), {'username': 'aaaaaa', 'password': 'bbbbbb'})
        self.assertEqual(status, 401)

    def test_auth_create_token_pair(self):
        """Test to create a token pair"""
        with self.app.app_context():
            status, data = self.post('{}/{}'.format(AUTH_URL, 'token-pair'),
                                     {'username': self.app.config.get('TEST_USER'),
                                      'password': self.app.config.get('TEST_USERS_PASSWORD')})
            self.assertEqual(status, 200)

#    def test_auth_try_create_second_token_pair(self):
#        """Test to create a second token pair for the same user"""
#        with self.app.app_context():
#            status, data = self.post('/api/auth/token-pair', {'username': self.app.config.get('TEST_USER'),
#                                                              'password': self.app.config.get('TEST_USERS_PASSWORD')})
#            self.assertEqual(status, 200)
#
#        with self.app.app_context():
#            status, data = self.post('/api/auth/token-pair', {'username': self.app.config.get('TEST_USER'),
#                                                              'password': self.app.config.get('TEST_USERS_PASSWORD')})
#        self.assertEqual(status, 403)

    def test_auth_create_pair_create_after_expired(self):
        """Test to create a second token pair after the first one has expired"""
        with self.app.app_context():
            status, data = self.post('{}/{}'.format(AUTH_URL, 'token-pair'),
                                     {'username': self.app.config.get('TEST_USER'),
                                      'password': self.app.config.get('TEST_USERS_PASSWORD')})
            self.assertEqual(status, 200)

            user = User.from_db(self.app.config.get('TEST_USER'))
            delta = datetime.timedelta(days=self.app.config.get('REFRESH_TOKEN_DURATION'))
            user.tokens[1].expiration_date = user.tokens[1].expiration_date - delta
            db.session.commit()

            status, data = self.post('{}/{}'.format(AUTH_URL, 'token-pair'),
                                     {'username': self.app.config.get('TEST_USER'),
                                      'password': self.app.config.get('TEST_USERS_PASSWORD')})
            self.assertEqual(status, 200)

    def test_auth_refresh_with_not_linked_token(self):
        """Test to refresh the access token with a wrong refresh token"""
        with self.app.app_context():
            status, data = self.post('{}/{}'.format(AUTH_URL, 'token-pair'),
                                     {'username': self.app.config.get('TEST_USER'),
                                      'password': self.app.config.get('TEST_USERS_PASSWORD')})
            access_token = data['access_token']['value']

            status, data = self.post('{}/{}/{}'.format(AUTH_URL, access_token, 'refresh'),
                                     {'refresh_token': 'not-linked'})
            self.assertEqual(status, 403)

    def test_auth_refresh_with_expired_token(self):
        """Test to refresh an access token with an expired refresh token"""
        with self.app.app_context():
            status, data = self.post('{}/{}'.format(AUTH_URL, 'token-pair'),
                                     {'username': self.app.config.get('TEST_USER'),
                                      'password': self.app.config.get('TEST_USERS_PASSWORD')})
            access_token = data['access_token']['value']
            refresh_token = data['refresh_token']['value']

            user = User.from_db(self.app.config.get('TEST_USER'))
            delta = datetime.timedelta(days=self.app.config.get('REFRESH_TOKEN_DURATION'))
            user.tokens[1].expiration_date = user.tokens[1].expiration_date - delta
            db.session.commit()

            status, data = self.post('{}/{}/{}'.format(AUTH_URL, access_token, 'refresh'),
                                     {'refresh_token': refresh_token})
            self.assertEqual(status, 403)

    def test_auth_refresh(self):
        """Test to refresh an access token"""
        with self.app.app_context():
            status, data = self.post('{}/{}'.format(AUTH_URL, 'token-pair'),
                                     {'username': self.app.config.get('TEST_USER'),
                                      'password': self.app.config.get('TEST_USERS_PASSWORD')})
            access_token = data['access_token']['value']
            refresh_token = data['refresh_token']['value']

            status, data = self.post('{}/{}/{}'.format(AUTH_URL, access_token, 'refresh'),
                                     {'refresh_token': refresh_token})
            self.assertEqual(status, 200)
