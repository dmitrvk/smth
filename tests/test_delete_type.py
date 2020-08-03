import logging
from unittest import mock

from pyfakefs import fake_filesystem_unittest

from smth import commands, db


class DeleteTypeTestCase(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        logging.disable()

        self.db = mock.MagicMock()
        self.db.notebooks_of_type_exist.return_value = False

        self.view = mock.MagicMock()
        self.view.ask_for_type.return_value = 'type'

    def test_delete_type(self):
        commands.TypesCommand(self.db, self.view).execute(['--delete'])
        self.db.delete_type_by_title.assert_called_once()

    def test_delete_type_no_answers(self):
        self.view.ask_for_type.return_value = ''
        commands.TypesCommand(self.db, self.view).execute(['--delete'])
        self.db.delete_type_by_title.assert_not_called()

    def test_delete_type_notebooks_of_type_exist(self):
        self.db.notebooks_of_type_exist.return_value = True
        commands.TypesCommand(self.db, self.view).execute(['--delete'])
        self.db.delete_type_by_title.assert_not_called()

    def test_delete_type_db_error(self):
        self.db.delete_type_by_title.side_effect = db.Error()
        command = commands.TypesCommand(self.db, self.view)
        self.assertRaises(SystemExit, command.execute, ['--delete'])
        self.view.show_error.assert_called()
