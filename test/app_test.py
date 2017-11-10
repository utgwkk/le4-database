import os
import unittest
import main


class AppTest(unittest.TestCase):
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

    def test_cannot_register_duplicated_username(self):
        self.register('alice', 'alicealice')

        res = self.register('alice', 'alicealice2')
        self.assertIn(b'has already taken', res.data)

    def test_follow_unfollow(self):
        self.register('alice', 'alicealice')
        self.logout()

        self.register('bobby', 'bobbobbob')
        self.logout()

        self.login('alice', 'alicealice')

        res = self.client.get('/@bobby')
        self.assertEqual(200, res.status_code)

        res = self.follow('bobby')
        self.assertIn(b'Follow successful', res.data)

        res = self.unfollow('bobby')
        self.assertIn(b'Unfollow successful', res.data)
    
    def test_upload(self):
        self.register('alice', 'alicealice')
        with open('./test/data/kids_chuunibyou_girl.png', 'rb') as f:
            res = self.upload(f, 'hoge', 'fuga')

    def test_favorite_post(self):
        self.register('alice', 'alicealice')
        with open('./test/data/kids_chuunibyou_girl.png', 'rb') as f:
            self.upload(f, 'hoge', 'fuga')
        self.logout()

        self.register('bobby', 'bobbobbob')

        # Can create a favorite
        res = self.favorite(1)
        self.assertIn(b'Unfavorite', res.data)

        # Can remove a favorite
        res = self.unfavorite(1)
        self.assertIn(b'Favorite', res.data)

    def test_list_favorite_post(self):
        self.register('alice', 'alicealice')
        for i in range(10):
            with open('./test/data/kids_chuunibyou_girl.png', 'rb') as f:
                self.upload(f, f'hoge{i}', f'fuga{i}')
        self.logout()

        self.register('bobby', 'bobbobbob')
        for i in range(10):
            self.favorite(i + 1)

        res = self.client.get('/favorites')
        for i in range(10):
            self.assertIn(b'hoge%d' % i, res.data)
            self.assertIn(b'fuga%d' % i, res.data)

    def test_delete_post(self):
        self.register('alice', 'alicealice')
        with open('./test/data/kids_chuunibyou_girl.png', 'rb') as f:
            self.upload(f, 'hoge', 'fuga')

        res = self.delete_post(1)
        self.assertIn(b'Delete successful', res.data)

    def test_delete_post_only_allowed_to_uploaded_user(self):
        self.register('alice', 'alicealice')
        with open('./test/data/kids_chuunibyou_girl.png', 'rb') as f:
            self.upload(f, 'hoge', 'fuga')

        self.register('bobby', 'bobbobbob')
        res = self.delete_post(1)
        self.assertEqual(403, res.status_code)


if __name__ == '__main__':
    unittest.main()
