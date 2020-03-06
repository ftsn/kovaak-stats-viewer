from tests import TestCaseApi


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
