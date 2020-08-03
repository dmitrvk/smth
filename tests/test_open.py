import logging
import unittest
from unittest import mock

from smth import commands, db, models


class OpenCommandTestCase(unittest.TestCase):
    def setUp(self):
        logging.disable()

        self.db = mock.MagicMock()
        self.view = mock.MagicMock()

    def test_execute(self):
        self.db.get_notebook_titles.return_value = ['notebook']

        notebook = models.Notebook('notebook', None, '/test/path.pdf')
        self.db.get_notebook_by_title.return_value = notebook

        self.view.ask_for_notebook.return_value = 'notebook'

        with mock.patch('subprocess.Popen') as popen_class:
            commands.OpenCommand(self.db, self.view).execute()
            popen_class.assert_called_once_with(['xdg-open', '/test/path.pdf'])

    def test_execute_db_error(self):
        self.db.get_notebook_titles.side_effect = db.Error('Failed')

        command = commands.OpenCommand(self.db, self.view)

        self.assertRaises(SystemExit, command.execute)
        self.view.show_error.assert_called_once_with('Failed')

    def test_execute_no_notebooks(self):
        self.db.get_notebook_titles.return_value = []

        with mock.patch('subprocess.Popen') as popen_class:
            commands.OpenCommand(self.db, self.view).execute()

            self.view.ask_for_notebook.assert_not_called()
            popen_class.assert_not_called()
