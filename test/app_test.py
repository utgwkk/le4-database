import os
import unittest
import main


class AppTest(unittest.TestCase):
    def setUp(self):
        main.app.testing = True
        self.client = main.app.test_client()
        os.environ['POSTGRESQL_DB'] = 'test_utgwkk'

    def tearDown(self):
        pass

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
