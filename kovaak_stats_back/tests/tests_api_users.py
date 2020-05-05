from tests import TestCaseApi
from kovaak_stats.models.user import User
from tests import app
from kovaak_stats.app import db
from werkzeug.datastructures import FileStorage
import datetime
import time

USERS_URL = '/api/users'


class TestApiUsers(TestCaseApi):
    def test_users_create(self):
        """Test to create a user"""
        status, data = self.post(USERS_URL, {'username': 'create_user',
                                             'email_addr': 'test@create.user',
                                             'password': 'test'})
        self.assertEqual(status, 200)

    def test_users_create_same_name(self):
        """Test to create a user with a name that already exists"""
        with self.app.app_context():
            status, data = self.post(USERS_URL, {'username': self.app.config.get('TEST_USER'),
                                                 'email_addr': 'test@create.user',
                                                 'password': 'test'})
            self.assertEqual(status, 400)

    def test_users_create_same_email_addr(self):
        """Test to create a user with an email address that already exists"""
        with self.app.app_context():
            status, data = self.post(USERS_URL, {'username': 'test@create.user',
                                                 'email_addr': self.app.config.get('TEST_USERS_EMAIL'),
                                                 'password': 'test'})
            self.assertEqual(status, 400)

    def test_users_get_all(self):
        """Test to get all the users"""
        status, data = self.get(USERS_URL)
        self.assertEqual(status, 200)

    def test_users_get_specific(self):
        """Test to get a user"""
        with self.app.app_context():
            status, data = self.get('{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER')))
            self.assertEqual(status, 200)

    def test_users_get_specific_non_existent(self):
        """Test to get a non-existent user"""
        status, data = self.get('{}/{}'.format(USERS_URL, 'non-existent'))
        self.assertEqual(status, 404)

    def test_users_modify(self):
        """Test to modify a user"""
        with self.app.app_context():
            changes = '[{"op": "replace","path": "/email_addr","value": "changed@email.addr"}]'
            status, data = self.patch('{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER')), {'changes': changes})
            self.assertEqual(data['email_addr'], 'changed@email.addr')
            self.assertEqual(status, 200)

    def test_users_modify_non_existent(self):
        """Test to modify a non-existent user"""
        status, data = self.patch('{}/{}'.format(USERS_URL, 'non-existent'), {'changes': ''})
        self.assertEqual(status, 404)

    def test_users_modify_badly_formatted_json(self):
        """Test to modify a user with a badly formatted JSON"""
        with self.app.app_context():
            changes = '[{"op": ,"path": "/email_addr","value": "changed@email.addr"}]'
            status, data = self.patch('{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER')), {'changes': changes})
            self.assertEqual(data['message'], 'Badly formatted JSON')
            self.assertEqual(status, 400)

    def test_users_modify_invalid_format(self):
        """Test to modify a user with an invalid JSON patch format"""
        with self.app.app_context():
            changes = '[{"op": "","path": "/email_addr","value": "changed@email.addr"}]'
            status, data = self.patch('{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER')), {'changes': changes})
            self.assertEqual(data['message'], "Invalid JSON patch format. More information: Unknown operation ''")
            self.assertEqual(status, 400)

    def test_users_modify_conflict(self):
        """Test to modify a user with a conflicting JSON patch"""
        with self.app.app_context():
            changes = '[{"op": "copy","from": "/non-existent","path": "/email_addr"}]'
            status, data = self.patch('{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER')), {'changes': changes})
            self.assertEqual(data['message'], "Conflict in the set of changes. More information: 'non-existent'")
            self.assertEqual(status, 409)

    def test_users_modify_invalid_values(self):
        """Test to modify a user with invalid values"""
        with self.app.app_context():
            changes = '[{"op": "add","path": "/rights/-","value": "users.lolilol"}]'
            status, data = self.patch('{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER')), {'changes': changes})
            error = "Invalid value(s) in the set of changes. More information: The right users.lolilol doesn't exist"
            self.assertEqual(data['message'], error)
            self.assertEqual(status, 400)

            changes = '[{"op": "add","path": "/rights/-","value": "users.create"}]'
            status, data = self.patch('{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER')), {'changes': changes})
            error = "Invalid value(s) in the set of changes. More information: {} already has the right users.create".format(self.app.config.get('TEST_USER'))
            self.assertEqual(data['message'], error)
            self.assertEqual(status, 400)

    def test_users_modify_no_list(self):
        """Test to modify a user without providing a list as parameter"""
        with self.app.app_context():
            changes = '{"op": "replace","path": "/email_addr","value": "changed@email.addr"}'
            status, data = self.patch('{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER')), {'changes': changes})
            error = "A JSON list following the JSON patch format is expected"
            self.assertEqual(data['message'], error)
            self.assertEqual(status, 400)

    def test_users_delete(self):
        """Test to delete a user"""
        with app.app_context():
            User.create('todelete', 'user.delete@lolilol.com', 'password')
            db.session.commit()
        status, data = self.delete('{}/{}'.format(USERS_URL, 'todelete'))
        self.assertEqual(status, 204)

    def test_users_delete_non_existent(self):
        """Test to delete a non existent user"""
        status, data = self.delete('{}/{}'.format(USERS_URL, 'non-existent'))
        self.assertEqual(status, 404)

    def test_users_get_users_rights(self):
        """Test to get the rights of a user"""
        with self.app.app_context():
            status, data = self.get('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'rights'))
            self.assertEqual(status, 200)

    def test_users_get_non_existent_users_rights(self):
        """Test to get the rights of a non existent user"""
        status, data = self.get('{}/{}/{}'.format(USERS_URL, 'non-existent', 'rights'))
        self.assertEqual(status, 404)

    def test_users_add_and_del_right_to_non_existent(self):
        """Test to delete and add a valid right to a non existent user"""
        status, data = self.delete('{}/{}/{}/{}'.format(USERS_URL, 'non-existent', 'rights', 'users.create'))
        self.assertEqual(status, 404)
        status, data = self.post('{}/{}/{}'.format(USERS_URL, 'non-existent', 'rights'),
                                 {'rights': 'users.create'})
        self.assertEqual(status, 404)

    def test_users_add_and_del_non_existent_right(self):
        """Test to delete and add a non existent right to a valid user"""
        with self.app.app_context():
            status, data = self.delete('{}/{}/{}/{}'.format(USERS_URL,
                                                            self.app.config.get('TEST_USER'),
                                                            'rights',
                                                            'non-existent'))
            self.assertEqual(status, 404)
            status, data = self.post('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'rights'),
                                     {'rights': 'non-existent'})
            self.assertEqual(status, 400)

    def test_users_add_and_del_right(self):
        """Test to delete and add a valid right to a valid user"""
        with self.app.app_context():
            status, data = self.delete('{}/{}/{}/{}'.format(USERS_URL,
                                                            self.app.config.get('TEST_USER'),
                                                            'rights',
                                                            'users.create'))
            self.assertEqual(status, 204)
            status, data = self.post('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'rights'),
                                     {'rights': 'users.create'})
            self.assertEqual(status, 204)

    def test_users_add_duplicate_right(self):
        """Test to add a right the user already has"""
        with self.app.app_context():
            status, data = self.post('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'rights'),
                                     {'rights': 'users.create'})
            self.assertEqual(status, 400)

    def test_users_del_non_owned_right(self):
        """Test to del a right the user doesn't have"""
        with self.app.app_context():
            self.delete('{}/{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'rights', 'users.create'))
            status, data = self.delete('{}/{}/{}/{}'.format(USERS_URL,
                                                            self.app.config.get('TEST_USER'),
                                                            'rights',
                                                            'users.create'))
            self.assertEqual(status, 400)

    def test_users_change_password_non_existent_user(self):
        """Test the password change procedure for a non existent user"""
        with self.app.app_context():
            status, data = self.get('{}/{}/{}'.format(USERS_URL, 'non-existent', 'recover'))
            self.assertEqual(status, 404)

            status, data = self.post('{}/{}/{}'.format(USERS_URL, 'non-existent', 'recover'),
                                     {'recovery_code': '123456', 'new_password': '123456'})
            self.assertEqual(status, 404)

    def test_users_try_generate_two_recover_codes(self):
        """Test to get two recover codes for a same user"""
        with self.app.app_context():
            self.get('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'recover'))
            status, data = self.get('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'recover'))
            self.assertEqual(status, 409)

    def test_users_full_password_change(self):
        """Test to change the password of the test user"""
        with self.app.app_context():
            status, data = self.get('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'recover'))
            user = User.from_db(self.app.config.get('TEST_USER'))
            code = user.recovery_code.value
            self.assertEqual(status, 204)

            status, data = self.post('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'recover'),
                                     {'recovery_code': code, 'new_password': '123456'})
            self.assertEqual(status, 204)

    def test_users_full_password_change_with_code_renewing(self):
        """Test to change the password of the test user after the 1st code has expired"""
        with app.app_context():
            self.get('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'recover'))
            user = User.from_db(self.app.config.get('TEST_USER'))
            delta = datetime.timedelta(minutes=self.app.config.get('RECOVERY_CODE_DURATION'))
            user.recovery_code.expiration_date = user.recovery_code.expiration_date - delta
            db.session.commit()
            self.get('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'recover'))
            user = User.from_db(self.app.config.get('TEST_USER'))
            code = user.recovery_code.value
            status, data = self.post('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'recover'),
                                     {'recovery_code': code, 'new_password': '123456'})
            self.assertEqual(status, 204)

    def test_users_change_password_wrong_code(self):
        """Test to change the password of the test user  but provide a wrong code"""
        with app.app_context():
            status, data = self.post('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'recover'),
                                     {'recovery_code': 'non-existent', 'new_password': '123456'})
            self.assertEqual(status, 403)

    def test_users_change_password_expired_code(self):
        """Test to change the password of the test user but provide an expired code"""
        with self.app.app_context():
            self.get('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'recover'))
            user = User.from_db(self.app.config.get('TEST_USER'))
            code = user.recovery_code.value
            delta = datetime.timedelta(minutes=self.app.config.get('RECOVERY_CODE_DURATION'))
            user.recovery_code.expiration_date = user.recovery_code.expiration_date - delta
            db.session.commit()
            status, data = self.post('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'recover'),
                                     {'recovery_code': code, 'new_password': '123456'})
            self.assertEqual(status, 403)

    def test_upload_stats_without_files(self):
        """Test to use the POST method on the stat route but without actually sending any files"""
        with app.app_context():
            status, data = self.post('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'stats'), {})
            self.assertEqual(status, 400)

    def test_upload_stats_non_existent_user(self):
        """Test to use the POST method on the stat route for a non-existent user"""
        file = FileStorage(
            stream=open('./tests/Close Long Strafes Invincible - Challenge - 2019.10.21-12.31.26 Stats.csv', "rb"),
            filename='./tests/Close Long Strafes Invincible - Challenge - 2019.10.21-12.31.26 Stats.csv',
            content_type='text/csv',
        )
        status, data = self.post('{}/{}/{}'.format(USERS_URL, 'non-existent', 'stats'), {'files': file})
        self.assertEqual(status, 404)

    def test_upload_stats(self):
        """Test to use the POST method on the stat route with a valid file"""
        file = FileStorage(
            stream=open('./tests/Close Long Strafes Invincible - Challenge - 2019.10.21-12.31.26 Stats.csv', "rb"),
            filename='./tests/Close Long Strafes Invincible - Challenge - 2019.10.21-12.31.26 Stats.csv',
            content_type='text/csv',
        )
        with app.app_context():
            status, data = self.post('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'stats'),
                                     {'files': file})
            self.assertEqual(status, 204)

    def test_upload_dup_stats(self):
        """Test to use the POST method on the stat route with a valid file"""
        with app.app_context():
            file = FileStorage(
                stream=open('./tests/Close Long Strafes Invincible - Challenge - 2019.10.21-12.31.26 Stats.csv', "rb"),
                filename='./tests/Close Long Strafes Invincible - Challenge - 2019.10.21-12.31.26 Stats.csv',
                content_type='text/csv',
            )
            status, data = self.post('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'stats'),
                                     {'files': file})
            self.assertEqual(status, 204)
            file = FileStorage(
                stream=open('./tests/Close Long Strafes Invincible - Challenge - 2019.10.21-12.31.26 Stats.csv', "rb"),
                filename='./tests/Close Long Strafes Invincible - Challenge - 2019.10.21-12.31.26 Stats.csv',
                content_type='text/csv',
            )
            status, data = self.post('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'stats'),
                                     {'files': file})
            self.assertEqual(status, 400)

    def test_upload_wrong_stats(self):
        """Test to use the POST method on the stat route with a valid file"""
        file = FileStorage(
            stream=open('./tests/wrong_file.csv', "rb"),
            filename='./tests/wrong_file.csv',
            content_type='text/csv',
        )
        with app.app_context():
            status, data = self.post('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'stats'),
                                     {'files': file})
            self.assertEqual(status, 400)

    def test_get_another_users_stats(self):
        """Test to access another user's stats"""
        status, data = self.post(USERS_URL, {'username': 'stats_user',
                                             'email_addr': 'test@stats.user',
                                             'password': 'test'})
        self.assertEqual(status, 200)
        file = FileStorage(
            stream=open('./tests/Close Long Strafes Invincible - Challenge - 2019.10.21-12.31.26 Stats.csv', "rb"),
            filename='./tests/Close Long Strafes Invincible - Challenge - 2019.10.21-12.31.26 Stats.csv',
            content_type='text/csv',
        )
        status, data = self.post('{}/{}/{}'.format(USERS_URL, 'stats_user', 'stats'), {'files': file})
        self.assertEqual(status, 403)
        status, data = self.get('{}/{}/{}'.format(USERS_URL, 'stats_user', 'stats'))
        self.assertEqual(status, 403)

    def test_get_stats(self):
        """Test to get all the stats for a user"""
        file = FileStorage(
            stream=open('./tests/Close Long Strafes Invincible - Challenge - 2019.10.21-12.31.26 Stats.csv', "rb"),
            filename='./tests/Close Long Strafes Invincible - Challenge - 2019.10.21-12.31.26 Stats.csv',
            content_type='text/csv',
        )
        with app.app_context():
            self.post('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'stats'), {'files': file})
            status, data = self.get('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'stats'))
            self.assertEqual(status, 200)
            self.assertEqual(len(data), 2)

    def test_get_stats_non_existent_user(self):
        """Test to get all the stats for a non-existent user"""
        status, data = self.get('{}/{}/{}'.format(USERS_URL, 'non-existent', 'stats'))
        self.assertEqual(status, 404)

    def test_get_filtered_stats(self):
        """Test to get all the stats for a user but using filters"""
        cur_timestamp = int(time.time())
        file = FileStorage(
            stream=open('./tests/Close Long Strafes Invincible - Challenge - 2019.10.21-12.31.26 Stats.csv', "rb"),
            filename='./tests/Close Long Strafes Invincible - Challenge - 2019.10.21-12.31.26 Stats.csv',
            content_type='text/csv',
        )
        with app.app_context():
            self.post('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'stats'), {'files': file})
            limit_timestamp = 2147483647
            status, data = self.get('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'stats'),
                                    data={'scenarii': ['non-existent']})
            self.assertEqual(status, 200)
            self.assertEqual(len(data), 1)

            status, data = self.get('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'stats'),
                                    data={'start': limit_timestamp})
            self.assertEqual(status, 200)
            self.assertEqual(len(data), 1)

            status, data = self.get('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'stats'),
                                    data={'start': cur_timestamp})
            self.assertEqual(status, 200)
            self.assertEqual(len(data), 2)

            status, data = self.get('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'stats'),
                                    data={'end': cur_timestamp})
            self.assertEqual(status, 200)
            self.assertEqual(len(data), 1)

            status, data = self.get('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'stats'),
                                    data={'end': limit_timestamp})
            self.assertEqual(status, 200)
            self.assertEqual(len(data), 2)

            status, data = self.get('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'stats'),
                                    data={'start': cur_timestamp, 'end': limit_timestamp})
            self.assertEqual(status, 200)
            self.assertEqual(len(data), 2)

            status, data = self.get('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'stats'),
                                    data={'start': limit_timestamp, 'end': cur_timestamp})
            self.assertEqual(status, 200)
            self.assertEqual(len(data), 1)

            status, data = self.get('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'stats'),
                                    data={'start': 'not a timestamp'})
            self.assertEqual(status, 400)
            self.assertEqual(len(data), 1)

            status, data = self.get('{}/{}/{}'.format(USERS_URL, self.app.config.get('TEST_USER'), 'stats'),
                                    data={'start': '1.1111'})
            self.assertEqual(status, 400)
            self.assertEqual(len(data), 1)


