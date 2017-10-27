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

    def register(self, username, password, description=''):
        return self.client.post('/register', data={
            'username': username,
            'password': password,
            'description': description,
        }, follow_redirects=True)

    def login(self, username, password):
        return self.client.post('/login', data={
            'username': username,
            'password': password,
        }, follow_redirects=True)

    def logout(self):
        self.client.post('/logout')

    def change_setting(self, description):
        return self.client.post('/setting', data={
            'description': description,
        }, follow_redirects=True)

    def test_index(self):
        self.client.get('/')

    def test_register(self):
        # Can register
        res = self.register('alice', 'alicealice', 'hey yo')
        self.assertIn(b'@alice', res.data)
        self.assertIn(b'hey yo', res.data)

        # Can logout and login again
        self.logout()
        res = self.login('alice', 'alicealice')
        self.assertIn(b'@alice', res.data)

    def test_change_setting(self):
        self.register('alice', 'alicealice')

        res = self.change_setting('hogefuga')
        self.assertIn(b'hogefuga', res.data)

    def test_not_logged_in(self):
        res = self.client.get('/mypage', follow_redirects=True)
        self.assertIn(b'You are not logged in', res.data)

        res = self.client.get('/setting', follow_redirects=True)
        self.assertIn(b'You are not logged in', res.data)


if __name__ == '__main__':
    unittest.main()
