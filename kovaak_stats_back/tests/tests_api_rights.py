from tests import TestCaseApi


class TestApiRights(TestCaseApi):
    def test_rights_get(self):
        """Test to get all the rights"""
        status, data = self.get('/api/rights')
        self.assertEqual(status, 200)

    def test_rights_get_non_existent(self):
        """Test to get a non existent right"""
        status, data = self.get('/api/rights/non-existent')
        self.assertEqual(status, 404)

    def test_rights_get_specific(self):
        """Test to get a specific right"""
        status, data = self.get('/api/rights/users.create')
        self.assertEqual(status, 200)

    def test_rights_create(self):
        """Test to create a right"""
        status, data = self.post('/api/rights', {'rights': 'titi.toto'})
        self.assertEqual(status, 200)

    def test_rights_create_already_existent(self):
        """Test to create a right that already exists"""
        status, data = self.post('/api/rights', {'rights': 'users.create'})
        self.assertEqual(status, 400)

    def test_rights_delete_non_existent(self):
        """Test to delete a non existent right"""
        status, data = self.delete('/api/rights/non-existent')
        self.assertEqual(status, 404)

    def test_rights_delete(self):
        """Test to delete a right previously created"""
        status, data = self.post('/api/rights', {'rights': 'titi.toto'})
        self.assertEqual(status, 200)

        status, data = self.delete('/api/rights/titi.toto')
        self.assertEqual(status, 204)
