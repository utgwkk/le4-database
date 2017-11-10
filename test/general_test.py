from test.app_testcase import AppTestCase


class GeneralTest(AppTestCase):
    def test_can_see_index(self):
        self.client.get('/')
