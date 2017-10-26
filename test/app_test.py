import os
import unittest
import main


class AppTest(unittest.TestCase):
    def setUp(self):
        main.app.testing = True
        self.client = main.app.test_client()
        self.initialize()

    def tearDown(self):
        self.initialize()

    def initialize(self):
        self.client.get('/initialize')

    def register(self, username, password):
        return self.client.post('/register', data={
            'username': username,
            'password': password,
        }, follow_redirects=True)

    def login(self, username, password):
        return self.client.post('/login', data={
            'username': username,
            'password': password,
        }, follow_redirects=True)

    def logout(self):
        self.client.post('/logout')

    def test_index(self):
        self.client.get('/')

    def test_register(self):
        # Can register
        res = self.register('alice', 'alicealice')
        self.assertIn(b'@alice', res.data)

        # Can logout and login again
        self.logout()
        res = self.login('alice', 'alicealice')
        self.assertIn(b'@alice', res.data)


if __name__ == '__main__':
    unittest.main()
