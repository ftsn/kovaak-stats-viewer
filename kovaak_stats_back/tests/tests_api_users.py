from tests import TestCaseApi
from kovaak_stats.models.user import User
from tests import app
from kovaak_stats.app import db
import datetime


class TestApiUsers(TestCaseApi):
    def test_users_create(self):
        """Test to create a user"""
        status, data = self.post('/api/users', {'username': 'create_user',
                                                'email_addr': 'test@create.user',
                                                'password': 'test'})
        self.assertEqual(status, 200)

    def test_users_create_same_name(self):
        """Test to create a user with a name that already exists"""
        status, data = self.post('/api/users', {'username': 'toto',
                                                'email_addr': 'test@create.user',
                                                'password': 'test'})
        self.assertEqual(status, 400)

    def test_users_create_same_email_addr(self):
        """Test to create a user with an email address that already exists"""
        status, data = self.post('/api/users', {'username': 'test@create.user',
                                                'email_addr': 'toto@toto.com',
                                                'password': 'test'})
        self.assertEqual(status, 400)

    def test_users_get_all(self):
        """Test to get all the users"""
        status, data = self.get('/api/users')
        self.assertEqual(status, 200)

    def test_users_get_specific(self):
        """Test to get a user"""
        status, data = self.get('/api/users/toto')
        self.assertEqual(status, 200)

    def test_users_get_specific_inexistent(self):
        """Test to get an inexistent user"""
        status, data = self.get('/api/users/inexistent-user')
        self.assertEqual(status, 404)

    def test_users_modify(self):
        """Test to modify a user"""
        changes = '[{"op": "replace","path": "/email_addr","value": "changed@email.addr"}]'
        status, data = self.patch('/api/users/toto', {'changes': changes})
        self.assertEqual(data['email_addr'], 'changed@email.addr')
        self.assertEqual(status, 200)

    def test_users_modify_inexistent(self):
        """Test to modify an inexistent user"""
        status, data = self.patch('/api/users/inexistent-user', {'changes': ''})
        self.assertEqual(status, 404)

    def test_users_modify_badly_formatted_json(self):
        """Test to modify a user with a badly formatted JSON"""
        changes = '[{"op": ,"path": "/email_addr","value": "changed@email.addr"}]'
        status, data = self.patch('/api/users/toto', {'changes': changes})
        self.assertEqual(data['message'], 'Badly formatted JSON')
        self.assertEqual(status, 400)

    def test_users_modify_invalid_format(self):
        """Test to modify a user with an invalid JSON patch format"""
        changes = '[{"op": "","path": "/email_addr","value": "changed@email.addr"}]'
        status, data = self.patch('/api/users/toto', {'changes': changes})
        self.assertEqual(data['message'], "Invalid JSON patch format. More information: Unknown operation ''")
        self.assertEqual(status, 400)

    def test_users_modify_conflict(self):
        """Test to modify a user with a conflicting JSON patch"""
        changes = '[{"op": "copy","from": "/non-existent","path": "/email_addr"}]'
        status, data = self.patch('/api/users/toto', {'changes': changes})
        self.assertEqual(data['message'], "Conflict in the set of changes. More information: 'non-existent'")
        self.assertEqual(status, 409)

    def test_users_modify_invalid_values(self):
        """Test to modify a user with invalid values"""
        changes = '[{"op": "add","path": "/rights/-","value": "users.lolilol"}]'
        status, data = self.patch('/api/users/toto', {'changes': changes})
        error = "Invalid value(s) in the set of changes. More information: The right users.lolilol doesn't exist"
        self.assertEqual(data['message'], error)
        self.assertEqual(status, 400)

        changes = '[{"op": "add","path": "/rights/-","value": "users.create"}]'
        status, data = self.patch('/api/users/toto', {'changes': changes})
        error = "Invalid value(s) in the set of changes. More information: toto already has the right users.create"
        self.assertEqual(data['message'], error)
        self.assertEqual(status, 400)

    def test_users_modify_no_list(self):
        """Test to modify a user without providing a list as parameter"""
        changes = '{"op": "replace","path": "/email_addr","value": "changed@email.addr"}'
        status, data = self.patch('/api/users/toto', {'changes': changes})
        error = "A JSON list following the JSON patch format is expected"
        self.assertEqual(data['message'], error)
        self.assertEqual(status, 400)

    def test_users_delete(self):
        """Test to delete a user"""
        with app.app_context():
            User.create('todelete', 'user.delete@lolilol.com', 'password')
            db.session.commit()
        status, data = self.delete('/api/users/todelete')
        self.assertEqual(status, 204)

    def test_users_delete_non_existent(self):
        """Test to delete a non existent user"""
        status, data = self.delete('/api/users/non-existent')
        self.assertEqual(status, 404)

    def test_users_get_users_rights(self):
        """Test to get the rights of a user"""
        status, data = self.get('/api/users/toto/rights')
        self.assertEqual(status, 200)

    def test_users_get_non_existent_users_rights(self):
        """Test to get the rights of a non existent user"""
        status, data = self.get('/api/users/non-existent/rights')
        self.assertEqual(status, 404)

    def test_users_add_and_del_right_to_non_existent(self):
        """Test to add and delete a valid right to a non existent user"""
        status, data = self.delete('/api/users/non-existent/rights/users.create')
        self.assertEqual(status, 404)

        status, data = self.post('/api/users/non-existent/rights', {'rights': 'users.create'})
        self.assertEqual(status, 404)

    def test_users_add_and_del_non_existent_right(self):
        """Test to add and delete a non existent right to a valid user"""
        status, data = self.delete('/api/users/toto/rights/non-existent')
        self.assertEqual(status, 404)

        status, data = self.post('/api/users/toto/rights', {'rights': 'non.existent'})
        self.assertEqual(status, 400)

    def test_users_add_and_del_right(self):
        """Test to add and delete a valid right to a valid user"""
        status, data = self.delete('/api/users/toto/rights/users.create')
        self.assertEqual(status, 204)

        status, data = self.post('/api/users/toto/rights', {'rights': 'users.create'})
        self.assertEqual(status, 204)

    def test_users_add_duplicate_right(self):
        """Test to add a right the user already has"""
        status, data = self.post('/api/users/toto/rights', {'rights': 'users.create'})
        self.assertEqual(status, 400)

    def test_users_del_non_owned_right(self):
        """Test to del a right the user doesn't have"""
        self.delete('/api/users/toto/rights/users.create')
        status, data = self.delete('/api/users/toto/rights/users.create')
        self.assertEqual(status, 400)

    def test_users_change_password_non_existent_user(self):
        """Test the password change procedure for a non existent user"""
        status, data = self.get('/api/users/non-existent/recover')
        self.assertEqual(status, 404)

        status, data = self.post('/api/users/non-existent/recover', {'recovery_code': '123456',
                                                                     'new_password': '123456'})
        self.assertEqual(status, 404)

    def test_users_try_generate_two_recover_codes(self):
        """Test to get two recover codes for a same user"""
        self.get('/api/users/toto/recover')
        status, data = self.get('/api/users/toto/recover')
        self.assertEqual(status, 409)

    def test_users_full_password_change(self):
        """Test to change the password of the user toto"""
        status, data = self.get('/api/users/toto/recover')
        with self.app.app_context():
            user = User.from_db(self.app.config.get('TEST_USER'))
            code = user.recovery_code.value
        self.assertEqual(status, 204)

        status, data = self.post('/api/users/toto/recover', {'recovery_code': code,
                                                             'new_password': '123456'})
        self.assertEqual(status, 204)

    def test_users_full_password_change_with_code_renewing(self):
        """Test to change the password of the user toto after the 1st code has expired"""
        status, data = self.get('/api/users/toto/recover')
        with app.app_context():
            user = User.from_db('toto')
            delta = datetime.timedelta(minutes=self.app.config.get('RECOVERY_CODE_DURATION'))
            user.recovery_code.expiration_date = user.recovery_code.expiration_date - delta
            db.session.commit()

        status, data = self.get('/api/users/toto/recover')
        with self.app.app_context():
            user = User.from_db(self.app.config.get('TEST_USER'))
            code = user.recovery_code.value

        status, data = self.post('/api/users/toto/recover', {'recovery_code': code,
                                                             'new_password': '123456'})
        self.assertEqual(status, 204)

    def test_users_change_password_wrong_code(self):
        """Test to change the password of the user toto but provide a wrong code"""
        status, data = self.post('/api/users/toto/recover', {'recovery_code': 'non-existent',
                                                             'new_password': '123456'})
        self.assertEqual(status, 403)

    def test_users_change_password_expired_code(self):
        """Test to change the password of the user toto but provide an expired code"""
        status, data = self.get('/api/users/toto/recover')
        with self.app.app_context():
            user = User.from_db(self.app.config.get('TEST_USER'))
            code = user.recovery_code.value
        with app.app_context():
            user = User.from_db('toto')
            delta = datetime.timedelta(minutes=self.app.config.get('RECOVERY_CODE_DURATION'))
            user.recovery_code.expiration_date = user.recovery_code.expiration_date - delta
            db.session.commit()

        status, data = self.post('/api/users/toto/recover', {'recovery_code': code,
                                                             'new_password': '123456'})
        self.assertEqual(status, 403)
