from flask import url_for

from web.tests import BaseTestCase


class UITest(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    # make sure that response code for /index is 200
    def test_index_reachable(self):
        with self.client.session_transaction() as sess:
            sess["user"] = "user"
        response = self.client.get(url_for('index_page.index'))
        self.assertEqual(response.status_code, 200)

    # make sure content of index page is properly loaded
    def test_index_page_loads(self):
        with self.client.session_transaction() as sess:
            sess["user"] = "user"
        response = self.client.get(url_for('index_page.index'))
        self.assertTrue(b'AVEditor tool' in response.data)