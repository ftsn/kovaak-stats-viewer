from tests import TestCaseApi
from tests import app
from kovaak_stats.app import db
from kovaak_stats.models.user import User
import datetime


class TestApiAuth(TestCaseApi):
    def test_auth_create_token_pair_wrong_credentials(self):
        """Test to create a token pair when providing wrong credentials"""
        status, data = self.post('/api/auth/token-pair', {'username': 'aaaaaa',
                                                          'password': 'bbbbbb'})
        self.assertEqual(status, 401)

    def test_auth_create_token_pair(self):
        """Test to create a token pair"""
        status, data = self.post('/api/auth/token-pair', {'username': 'toto',
                                                          'password': 'titi'})
        self.assertEqual(status, 200)

    def test_auth_try_create_second_token_pair(self):
        """Test to create a second token pair for the same user"""
        status, data = self.post('/api/auth/token-pair', {'username': 'toto',
                                                          'password': 'titi'})
        self.assertEqual(status, 200)

        #status, data = self.post('/api/auth/token-pair', {'username': 'toto',
        #                                                  'password': 'titi'})
        #self.assertEqual(status, 403)

    def test_auth_create_pair_create_after_expired(self):
        """Test to create a second token pair after the first one has expired"""
        status, data = self.post('/api/auth/token-pair', {'username': 'toto',
                                                          'password': 'titi'})
        self.assertEqual(status, 200)
        with app.app_context():
            user = User.from_db('toto')
            delta = datetime.timedelta(days=self.app.config.get('REFRESH_TOKEN_DURATION'))
            user.tokens[1].expiration_date = user.tokens[1].expiration_date - delta
            db.session.commit()

        status, data = self.post('/api/auth/token-pair', {'username': 'toto',
                                                          'password': 'titi'})
        self.assertEqual(status, 200)

    def test_auth_refresh_with_not_linked_token(self):
        """Test to refresh the access token with a wrong refresh token"""
        status, data = self.post('/api/auth/token-pair', {'username': 'toto',
                                                          'password': 'titi'})
        access_token = data['access_token']['value']

        status, data = self.post('/api/auth/{}/refresh'.format(access_token), {'refresh_token': 'not-linked'})
        self.assertEqual(status, 403)

    def test_auth_refresh_with_expired_token(self):
        """Test to refresh an access token with an expired refresh token"""
        status, data = self.post('/api/auth/token-pair', {'username': 'toto',
                                                          'password': 'titi'})
        access_token = data['access_token']['value']
        refresh_token = data['refresh_token']['value']
        with app.app_context():
            user = User.from_db('toto')
            delta = datetime.timedelta(days=self.app.config.get('REFRESH_TOKEN_DURATION'))
            user.tokens[1].expiration_date = user.tokens[1].expiration_date - delta
            db.session.commit()

        status, data = self.post('/api/auth/{}/refresh'.format(access_token), {'refresh_token': refresh_token})
        self.assertEqual(status, 403)

    def test_auth_refresh(self):
        """Test to refresh an access token"""
        status, data = self.post('/api/auth/token-pair', {'username': 'toto',
                                                          'password': 'titi'})
        access_token = data['access_token']['value']
        refresh_token = data['refresh_token']['value']

        status, data = self.post('/api/auth/{}/refresh'.format(access_token), {'refresh_token': refresh_token})
        self.assertEqual(status, 200)
