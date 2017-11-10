import os
import unittest
import main


class AppTestCase(unittest.TestCase):
    def setUp(self):
        main.app.testing = True
        main.app.config['UPLOAD_FOLDER'] = os.environ['TEST_UPLOAD_FOLDER']
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

    def follow(self, username):
        return self.client.post('/follow', data={
            'username': username
        }, follow_redirects=True)

    def unfollow(self, username):
        return self.client.post('/unfollow', data={
            'username': username
        }, follow_redirects=True)


    def upload(self, file, title, description):
        return self.client.post('/upload', data={
            'file': file,
            'title': title,
            'description': description
        }, follow_redirects=True)

    def favorite(self, post_id):
        return self.client.post(
            f'/favorite/{post_id}', follow_redirects=True
        )

    def unfavorite(self, post_id):
        return self.client.post(
            f'/unfavorite/{post_id}', follow_redirects=True
        )

    def delete_post(self, post_id):
        return self.client.post(
            f'/post/{post_id}/delete', follow_redirects=True
        )
