from test.app_testcase import AppTestCase


class EventTest(AppTestCase):
    def test_only_logged_in_user_can_see_event_page(self):
        res = self.client.get('/events')
        self.assertNotEqual(200, res.status_code)

    def test_logged_in_user_can_see_event_page(self):
        self.register('alice', 'alicealice')
        res = self.client.get('/events')
        self.assertEqual(200, res.status_code)
