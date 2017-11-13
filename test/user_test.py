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

    def test_logout(self):
        self.register('alice', 'alicealice', 'hey yo')
        res = self.logout()
        self.assertNotIn(b'@alice', res.data)

    def test_username_should_be_longer_than_3_chars(self):
        # Too short username
        res = self.register('bob', 'bobbobbob')
        self.assertNotIn(b'@bob', res.data)

    def test_username_should_be_shorter_than_32_chars(self):
        # Too long username
        res = self.register('thisusernamehasmorethan32characters', 'hogefuga')
        self.assertNotIn(b'@thisusernamehasmorethan32characters', res.data)

    def test_password_should_be_longer_than_5_chars(self):
        # Too short password
        res = self.register('bobby', 'short')
        self.assertNotIn(b'@bobby', res.data)

    def test_user_not_found_should_be_404(self):
        res = self.client.get('/@notfound')
        self.assertEqual(404, res.status_code)

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

    def test_cannot_login_with_wrong_password(self):
        self.register('alice', 'alicealice')

        res = self.login('alice', 'alicealice2')
        self.assertIn(b'Login failed', res.data)

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

    def test_following_list(self):
        self.register('alice', 'alicealice')
        self.logout()

        self.register('bobby', 'bobbobbob')
        self.logout()

        self.login('alice', 'alicealice')
        self.follow('bobby')

        res = self.client.get('/following', follow_redirects=True)
        self.assertIn(b'bobby', res.data)

    def test_follower_list(self):
        self.register('alice', 'alicealice')
        self.logout()

        self.register('bobby', 'bobbobbob')
        self.logout()

        self.login('alice', 'alicealice')
        self.follow('bobby')
        self.logout()

        self.login('bobby', 'bobbobbob')

        res = self.client.get('/follower', follow_redirects=True)
        self.assertIn(b'alice', res.data)

    def test_other_users_following_list(self):
        self.register('alice', 'alicealice')
        self.logout()

        self.register('bobby', 'bobbobbob')
        self.follow('alice')
        self.logout()

        self.login('alice', 'alicealice')

        res = self.client.get('/@bobby/following', follow_redirects=True)
        self.assertIn(b'alice', res.data)

    def test_other_users_follower_list(self):
        self.register('alice', 'alicealice')
        self.logout()

        self.register('bobby', 'bobbobbob')
        self.logout()

        self.login('alice', 'alicealice')
        self.follow('bobby')

        res = self.client.get('/@bobby/follower', follow_redirects=True)
        self.assertIn(b'alice', res.data)
