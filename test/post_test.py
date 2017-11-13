from test.app_testcase import AppTestCase


class PostTest(AppTestCase):
    def test_upload(self):
        self.register('alice', 'alicealice')
        with open('./test/data/kids_chuunibyou_girl.png', 'rb') as f:
            res = self.upload(f, 'hoge', 'fuga')
        self.assertIn(b'hoge', res.data)
        self.assertIn(b'fuga', res.data)

        # Check uploaded image
        res = self.client.get('/post/1/image')
        self.assertEqual(200, res.status_code)
        self.assertGreater(len(res.data), 0)

    def test_upload_without_file_will_fail(self):
        self.register('alice', 'alicealice')
        res = self.upload(None, 'hoge', 'fuga')
        self.assertIn(b'No file specified', res.data)

    def test_visit_upload_page(self):
        self.register('alice', 'alicealice')

        res = self.client.get('/upload', follow_redirects=True)
        self.assertNotIn(b'You are not logged in', res.data)

    def test_only_logged_in_user_can_visit_upload_page(self):
        res = self.client.get('/upload', follow_redirects=True)
        self.assertIn(b'You are not logged in', res.data)

    def test_post_list(self):
        self.register('alice', 'alicealice')
        with open('./test/data/kids_chuunibyou_girl.png', 'rb') as f:
            res = self.upload(f, 'hoge', 'fuga')

        # Check uploaded image is listed on /posts
        res = self.client.get('/posts')
        self.assertIn(b'hoge', res.data)
        self.assertIn(b'fuga', res.data)

    def test_only_logged_in_user_can_see_upload_page(self):
        res = self.client.get('/upload', follow_redirects=True)
        self.assertIn(b'You are not logged in', res.data)

    def test_post_owner_can_delete_post(self):
        self.register('alice', 'alicealice')
        with open('./test/data/kids_chuunibyou_girl.png', 'rb') as f:
            self.upload(f, 'hoge', 'fuga')

        res = self.delete_post(1)
        self.assertIn(b'Delete successful', res.data)

    def test_delete_post_only_allowed_to_post_owner(self):
        self.register('alice', 'alicealice')
        with open('./test/data/kids_chuunibyou_girl.png', 'rb') as f:
            self.upload(f, 'hoge', 'fuga')

        self.register('bobby', 'bobbobbob')
        res = self.delete_post(1)
        self.assertEqual(403, res.status_code)

    def test_can_see_uploaded_post_on_user_page(self):
        self.register('alice', 'alicealice')
        with open('./test/data/kids_chuunibyou_girl.png', 'rb') as f:
            self.upload(f, 'hoge', 'fuga')
        self.logout()

        res = self.client.get('/@alice', follow_redirects=True)
        self.assertIn(b'hoge', res.data)
        self.assertIn(b'fuga', res.data)
