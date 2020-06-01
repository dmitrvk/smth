import unittest
from unittest import mock

from smth import views
from tests import testutils


class TestView(unittest.TestCase):
    """Test user interface."""

    def setUp(self):
        self.view = views.CLIView()

    @mock.patch('inquirer.prompt', return_value={'answer': 'test'})
    def test_ask_for_new_notebook_info(self, prompt):
        validator = mock.MagicMock()
        validator.validate_title.return_value = True
        validator.validate_type.return_value = True
        validator.validate_path.return_value = True
        validator.validate_first_page_number.return_value = True

        answers = self.view.ask_for_new_notebook_info([], validator)

        self.assertDictEqual(answers, {'answer': 'test'})

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

