import unittest
from unittest import mock

from smth import scanner, view
from tests import testutils


class ViewTestCase(unittest.TestCase):
    def setUp(self):
        self.view = view.View()

    def test_ask_for_new_notebook_info(self):
        answers = {
            'title': 'notebook',
            'type': 'A4',
            'path': '/test/path.pdf',
            'first_page_number': 1,
        }

        with mock.patch('PyInquirer.prompt', return_value=answers):
            validator = mock.MagicMock(**{
                'validate_title.return_value': True,
                'validate_type.return_value': True,
                'validate_path.return_value': True,
                'validate_first_page_number.return_value': True,
            })

            actual_answers = self.view.ask_for_new_notebook_info([], validator)

            self.assertDictEqual(actual_answers, answers)

    def test_ask_for_new_notebook_info_no_answer(self):
        with mock.patch('PyInquirer.prompt', return_value=None):
            validator = mock.MagicMock(**{
                'validate_title.return_value': True,
                'validate_type.return_value': True,
                'validate_path.return_value': True,
                'validate_first_page_number.return_value': True,
            })

            answers = self.view.ask_for_new_notebook_info([], validator)

            self.assertDictEqual(answers, {})

    def test_ask_for_new_type_info(self):
        answers = {
            'title': 'type',
            'page_width': '100',
            'page_height': '200',
            'pages_paired': False,
        }

        with mock.patch('PyInquirer.prompt', return_value=answers):
            validator = mock.MagicMock(**{
                'validate_title.return_value': True,
                'validate_page_size.return_value': True,
            })

            actual_answers = self.view.ask_for_new_type_info(validator)

            self.assertDictEqual(actual_answers, {
                'title': 'type',
                'page_width': 100,
                'page_height': 200,
                'pages_paired': False,
            })

    def test_ask_for_new_type_info_no_answer(self):
        with mock.patch('PyInquirer.prompt', return_value=None):
            validator = mock.MagicMock(**{
                'validate_title.return_value': True,
                'validate_page_size.return_value': True,
            })

            answers = self.view.ask_for_new_type_info(validator)

            self.assertDictEqual(answers, {})

    def test_ask_for_device(self):
        devices = [
            scanner.Device('name 1', 'vendor 1', 'model 1', 'type 1'),
            scanner.Device('name 2', 'vendor 2', 'model 2', 'type 2'),
        ]

        answers = {
            'device': 'name 1',
        }

        with mock.patch('PyInquirer.prompt', return_value=answers):
            chosen_device = self.view.ask_for_device(devices)

        self.assertEqual(chosen_device, answers['device'])

    def test_ask_for_device_no_answer(self):
        devices = [
            scanner.Device('name 1', 'vendor 1', 'model 1', 'type 1'),
            scanner.Device('name 2', 'vendor 2', 'model 2', 'type 2'),
        ]

        with mock.patch('PyInquirer.prompt', return_value=None):
            chosen_device = self.view.ask_for_device(devices)

        self.assertEqual(chosen_device, '')

    def test_ask_for_notebook(self):
        notebooks = ['notebook 1', 'notebook 2', 'notebook 3']

        answers = {
            'notebook': 'notebook 1',
        }

        with mock.patch('PyInquirer.prompt', return_value=answers):
            notebook = self.view.ask_for_notebook(notebooks)

        self.assertEqual(notebook, answers['notebook'])

    def test_ask_for_notebook_no_answer(self):
        notebooks = ['notebook 1', 'notebook 2', 'notebook 3']

        with mock.patch('PyInquirer.prompt', return_value=None):
            notebook = self.view.ask_for_notebook(notebooks)

        self.assertEqual(notebook, '')

    def test_ask_for_pages_to_append(self):
        answers = {
            'append': '3',
        }

        validator = mock.MagicMock(**{
            'validate_number_of_pages_to_append.return_value': True,
        })

        with mock.patch('PyInquirer.prompt', return_value=answers):
            answer = self.view.ask_for_pages_to_append(validator)

        self.assertEqual(answer, 3)

    def test_ask_for_pages_to_append_no_answer(self):
        validator = mock.MagicMock(**{
            'validate_number_of_pages_to_append.return_value': True,
        })

        with mock.patch('PyInquirer.prompt', return_value=None):
            answer = self.view.ask_for_pages_to_append(validator)

        self.assertEqual(answer, 0)

    def test_ask_for_pages_to_append_empty_answer(self):
        answers = {
            'append': ' ',
        }

        validator = mock.MagicMock(**{
            'validate_number_of_pages_to_append.return_value': True,
        })

        with mock.patch('PyInquirer.prompt', return_value=answers):
            answer = self.view.ask_for_pages_to_append(validator)

        self.assertEqual(answer, 0)

    def test_ask_for_pages_to_replace(self):
        answers = {
            'replace': ' 1 2  3-6 4-7  '
                }
        validator = mock.MagicMock(**{
            'validate_pages_to_replace.return_value': True,
        })

        with mock.patch('PyInquirer.prompt', return_value=answers):
            answer = self.view.ask_for_pages_to_replace(validator)

        self.assertListEqual(answer, ['1', '2', '3-6', '4-7'])

    def test_ask_for_pages_to_replace_no_answer(self):
        validator = mock.MagicMock(**{
            'validate_pages_to_replace.return_value': True,
        })

        with mock.patch('PyInquirer.prompt', return_value=None):
            answer = self.view.ask_for_pages_to_replace(validator)

        self.assertListEqual(answer, [])

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

    def test_confirm(self):
        with mock.patch('PyInquirer.prompt', return_value={'answer': True}):
            answer = self.view.confirm('question')
            self.assertTrue(answer)

        with mock.patch('PyInquirer.prompt', return_value={'answer': False}):
            answer = self.view.confirm('question')
            self.assertFalse(answer)

        with mock.patch('PyInquirer.prompt', return_value=None):
            answer = self.view.confirm('question')
            self.assertFalse(answer)

    def test_show_info(self):
        message = 'Test message'
        output = testutils.capture_stdout(self.view.show_info, message)
        self.assertEqual(output, f'{message}\n')

    def test_show_error(self):
        message = 'Test message'
        output = testutils.capture_stderr(self.view.show_error, message)
        self.assertEqual(output, f'{message}\n')

    def test_show_separator(self):
        output = testutils.capture_stdout(self.view.show_separator)
        self.assertEqual(output, '----------------------------------------\n')
