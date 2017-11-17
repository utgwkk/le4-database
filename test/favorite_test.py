from test.app_testcase import AppTestCase


class FavoriteTest(AppTestCase):
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

    def test_cannot_favorite_not_exist_post(self):
        self.register('alice', 'alicealice')
        res = self.favorite(1)
        self.assertEqual(400, res.status_code)

    def test_list_favorite_post(self):
        self.register('alice', 'alicealice')
        for i in range(10):
            with open('./test/data/kids_chuunibyou_girl.png', 'rb') as f:
                self.upload(f, f'hoge{i}', f'fuga{i}')
        self.logout()

        self.register('bobby', 'bobbobbob')
        for i in range(10):
            self.favorite(i + 1)

        res = self.client.get('/favorites', follow_redirects=True)
        for i in range(10):
            self.assertIn(b'hoge%d' % i, res.data)
            self.assertIn(b'fuga%d' % i, res.data)
