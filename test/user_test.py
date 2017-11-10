from test.app_testcase import AppTestCase


class UserTest(AppTestCase):
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
