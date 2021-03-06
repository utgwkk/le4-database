from test.app_testcase import AppTestCase


class CommentTest(AppTestCase):
    def test_post_comment(self):
        self.register('alice', 'alicealice')
        with open('./test/data/kids_chuunibyou_girl.png', 'rb') as f:
            self.upload(f, 'hoge', 'fuga')
        self.logout()

        self.register('bobby', 'bobbobbob')
        res = self.client.post('/post/1/comment', data={
            'content': 'POYO'
        }, follow_redirects=True)
        self.assertIn(b'POYO', res.data)

    def test_cannot_comment_when_not_logged_in(self):
        self.register('alice', 'alicealice')
        with open('./test/data/kids_chuunibyou_girl.png', 'rb') as f:
            self.upload(f, 'hoge', 'fuga')
        self.logout()

        res = self.client.post('/post/1/comment', data={
            'content': 'POYO'
        }, follow_redirects=True)
        self.assertIn(b'You are not logged in', res.data)

    def test_cannot_comment_to_not_exist_post(self):
        self.register('alice', 'alicealice')

        res = self.client.post('/post/1/comment', data={
            'content': 'POYO'
        }, follow_redirects=True)
        self.assertEqual(400, res.status_code)
