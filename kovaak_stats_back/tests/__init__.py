import os
import unittest
import json
from base64 import b64encode
from flask import g, current_app
from kovaak_stats.app import create_app, db
from kovaak_stats.models.user import User
from kovaak_stats.models.right import Right

app = create_app(config='../tests/app.conf')
rights = [
    'users.create',
    'users.del',
    'users.modify',
    'users.get',
    'users.rights_add',
    'users.rights_del',
    'users.rights_get',
    'rights.create',
    'rights.del',
    'rights.get'
]


class TestCaseApi(unittest.TestCase):
    def setUp(self):
        self.app = app
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            if os.path.isfile('./tests/app.conf'):
                self.app.config.from_pyfile('../tests/app.conf')
            # Create our test user
            user = User.create(self.app.config.get('TEST_USER'),
                               self.app.config.get('TEST_USERS_EMAIL'),
                               self.app.config.get('TEST_USERS_PASSWORD'))
            for right_name in rights:
                user.rights.append(Right.create(right_name))
            db.session.add(user)
            self._basic = b64encode('{0}:{1}'.format(self.app.config.get('TEST_USER'),
                                                     self.app.config.get('TEST_USERS_PASSWORD')).encode('utf8')).decode('utf8')
            g.current_user = None
            db.session.commit()

    def tearDown(self):
        # Delete our test user
        with self.app.app_context():
            if os.path.isfile('./tests/app.conf'):
                self.app.config.from_pyfile('../tests/app.conf')
            user = User.from_db(self.app.config.get('TEST_USER'))
            if user:
                user.delete()
            db.session.remove()
            db.drop_all()

    def get(self, endpoint, authorization=None, headers={}):
        if authorization:
            if authorization != 'noauth':
                headers['Authorization'] = authorization
        else:
            headers['Authorization'] = 'Basic {0}'.format(self._basic)
        headers['Accept'] = 'application/javascript'

        with self.app.app_context():
            rv = self.app.test_client().get(endpoint, headers=headers)
        status = int(rv.status.split(' ')[0])
        if rv.data:
            return status, json.loads(rv.data.decode('utf8'))
        return status, None

    def post(self, endpoint, data, authorization=None, headers={}):
        if authorization:
            headers['Authorization'] = authorization
        else:
            headers['Authorization'] = 'Basic {0}'.format(self._basic)
        headers['Accept'] = 'application/javascript'

        with self.app.app_context():
            rv = self.app.test_client().post(endpoint, data=data, headers=headers)
        status = int(rv.status.split(' ')[0])
        if rv.data:
            return status, json.loads(rv.data.decode('utf8'))
        return status, None

    def patch(self, endpoint, data, authorization=None, headers={}):
        if authorization:
            headers['Authorization'] = authorization
        else:
            headers['Authorization'] = 'Basic {0}'.format(self._basic)
        headers['Accept'] = 'application/javascript'

        with self.app.app_context():
            rv = self.app.test_client().patch(endpoint, data=data, headers=headers)
        status = int(rv.status.split(' ')[0])
        if rv.data:
            return status, json.loads(rv.data.decode('utf8'))
        return status, None

    def put(self, endpoint, data, authorization=None, headers={}):
        if authorization:
            headers['Authorization'] = authorization
        else:
            headers['Authorization'] = 'Basic {0}'.format(self._basic)
        headers['Accept'] = 'application/javascript'

        with self.app.app_context():
            rv = self.app.test_client().put(endpoint, data=data, headers=headers)
        status = int(rv.status.split(' ')[0])
        if rv.data:
            return status, json.loads(rv.data.decode('utf8'))
        return status, None

    def delete(self, endpoint, authorization=None, headers={}):
        if authorization:
            headers['Authorization'] = authorization
        else:
            headers['Authorization'] = 'Basic {0}'.format(self._basic)
        headers['Accept'] = 'application/javascript'

        with self.app.app_context():
            rv = self.app.test_client().delete(endpoint, headers=headers)
        status = int(rv.status.split(' ')[0])
        self.assertNotEqual(status, 401)
        if rv.data:
            return status, json.loads(rv.data.decode('utf8'))
        else:
            return status, None


if __name__ == '__main__':
    unittest.main()
