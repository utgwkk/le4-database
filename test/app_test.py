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

    def test_index(self):
        self.client.get('/')

    def test_register(self):
        res = self.client.post('/register', data={
            'username': 'alice',
            'password': 'alicealice',
        }, follow_redirects=True)
        self.assertIn(b'@alice', res.data)


if __name__ == '__main__':
    unittest.main()
