import unittest
from unittest import mock

from smth import view
from tests import testutils


class ViewTestCase(unittest.TestCase):
    def setUp(self):
        self.view = view.View()

    def test_ask_for_new_notebook_info(self):
        answers_mock = {'answer': 'test'}

        with mock.patch('PyInquirer.prompt', return_value=answers_mock):
            validator = mock.MagicMock()
            validator.validate_title.return_value = True
            validator.validate_type.return_value = True
            validator.validate_path.return_value = True
            validator.validate_first_page_number.return_value = True

            answers = self.view.ask_for_new_notebook_info([], validator)

            self.assertDictEqual(answers, answers_mock)

    def test_ask_for_scan_prefs(self):
        answers = {
            'notebook': 'test',
            'append': '3',
        }

        with mock.patch('PyInquirer.prompt', return_value=answers):
            validator = mock.MagicMock()
            validator.validate_number_of_pages_to_append.return_value = True

            actual_answers = self.view.ask_for_scan_prefs([], validator)

            self.assertDictEqual(actual_answers, answers)

    def test_show_notebooks(self):
        notebooks = []

        for i in range(3):
            notebook = mock.MagicMock()
            notebook.title = f'Test{i}'
            notebook.total_pages = i ** 2
            notebook.type = mock.MagicMock()
            notebook.type.title = 'Test Type'
            notebooks.append(notebook)

        output = testutils.capture_stdout(self.view.show_notebooks, notebooks)

        for i in range(3):
            self.assertIn(f'Test{i}', output)
            self.assertIn(str(i ** 2), output)
            self.assertIn('Test Type', output)

        # No notebooks
        output = testutils.capture_stdout(self.view.show_notebooks, [])
        self.assertIn('No notebooks found', output)

    def test_show_types(self):
        types = []

        for i in range(3):
            type = mock.MagicMock()
            type.title = f'Test{i}'
            type.page_width = i ** 2 * 100
            type.page_height = i ** 3 * 100
            types.append(type)

        output = testutils.capture_stdout(self.view.show_types, types)

        for i in range(3):
            self.assertIn(f'Test{i}', output)
            size = '{}x{}mm'.format(str(i ** 2 * 100), str(i ** 3 * 100))
            self.assertIn(size, output)

        # No types
        output = testutils.capture_stdout(self.view.show_types, [])
        self.assertIn('No types found', output)

    def test_show_info(self):
        message = 'Test message'
        output = testutils.capture_stdout(self.view.show_info, message)
        self.assertEqual(output, f'{message}\n')

    def test_show_error(self):
        message = 'Test message'
        output = testutils.capture_stderr(self.view.show_error, message)
        self.assertEqual(output, f'{message}\n')
