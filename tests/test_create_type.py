import logging
from unittest import mock

from pyfakefs import fake_filesystem_unittest

from smth import commands, db


class CreateTypeTestCase(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        logging.disable()

        self.db = mock.MagicMock()
        self.view = mock.MagicMock()

        self.answers = {
            'title': 'notebook',
            'page_width': 100,
            'page_height': 200,
            'pages_paired': True,
        }

        self.view.ask_for_new_type_info.return_value = self.answers

    def test_create_type(self):
        commands.TypesCommand(self.db, self.view).execute(['--create'])
        self.db.save_type.assert_called_once()

    def test_create_type_no_answers(self):
        self.view.ask_for_new_type_info.return_value = None
        commands.TypesCommand(self.db, self.view).execute(['--create'])
        self.db.save_type.assert_not_called()

    def test_create_type_db_error(self):
        self.db.save_type.side_effect = db.Error('Fail')
        command = commands.TypesCommand(self.db, self.view)
        self.assertRaises(SystemExit, command.execute, ['--create'])
        self.view.show_error.assert_called_once_with('Fail')
