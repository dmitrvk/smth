import unittest
from unittest import mock

from smth import views
from tests import testutils


class TestScanView(unittest.TestCase):
    """Test user interface."""

    def test_ask_for_scan_prefs(self):
        view = views.ScanView()

        answers = {'answer': 'test'}

        with mock.patch('inquirer.prompt', return_value=answers):
            validator = mock.MagicMock()
            validator.test_validate_number_of_pages_to_append.return_value=True

            answers = view.ask_for_scan_prefs([], [], validator)

            self.assertDictEqual(answers, {'answer': 'test'})

