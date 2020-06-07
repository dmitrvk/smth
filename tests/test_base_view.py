import unittest

from smth import views
from tests import testutils


class TestBaseView(unittest.TestCase):
    def setUp(self):
        self.view = views.BaseView()

    def test_show_info(self):
        message = 'Test message'
        output = testutils.capture_stdout(self.view.show_info, message)
        self.assertEqual(output, f'{message}\n')

    def test_show_error(self):
        message = 'Test message'
        output = testutils.capture_stderr(self.view.show_error, message)
        self.assertEqual(output, f'{message}\n')
