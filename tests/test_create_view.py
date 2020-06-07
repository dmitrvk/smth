import unittest
from unittest import mock

from smth import views


class TestCreateView(unittest.TestCase):
    def test_ask_for_new_notebook_info(self):
        view = views.CreateView()

        answers_mock = {'answer': 'test'}

        with mock.patch('inquirer.prompt', return_value=answers_mock):
            validator = mock.MagicMock()
            validator.validate_title.return_value = True
            validator.validate_type.return_value = True
            validator.validate_path.return_value = True
            validator.validate_first_page_number.return_value = True

            answers = view.ask_for_new_notebook_info([], validator)

            self.assertDictEqual(answers, answers_mock)
