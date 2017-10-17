import unittest
import main


class AppTest(unittest.TestCase):
    def setUp(self):
        main.app.testing = True
        self.client = main.app.test_client()

    def tearDown(self):
        pass

    def test_index(self):
        self.client.get('/')


if __name__ == '__main__':
    unittest.main()
