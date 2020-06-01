import unittest
from unittest import mock

from smth import views
from tests import testutils


class TestView(unittest.TestCase):
    """Test user interface."""

    def setUp(self):
        self.view = views.CLIView()

    @mock.patch('inquirer.prompt', return_value={'answer': 'test'})
    def test_ask_for_scan_prefs(self, prompt):
        validator = mock.MagicMock()
        validator.test_validate_number_of_pages_to_append.return_value=True

        answers = self.view.ask_for_scan_prefs([], [], validator)

        self.assertDictEqual(answers, {'answer': 'test'})

    def test_show_info(self):
        output = testutils.capture_stdout(self.view.show_info, 'Test Info')
        self.assertEqual(output, 'Test Info\n')

    def test_show_error(self):
        output = testutils.capture_stderr(self.view.show_error, 'Test Error')
        self.assertEqual(output, 'Test Error\n')

