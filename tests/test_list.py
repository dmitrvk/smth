import logging
import unittest
from unittest import mock

from smth import commands, db


class ListCommandTestCase(unittest.TestCase):
    def setUp(self):
        logging.disable()

        self.db = mock.MagicMock()
        self.view = mock.MagicMock()

    def test_execute(self):
        self.db.get_notebooks.return_value = []

        commands.ListCommand(self.db, self.view).execute()

        self.db.get_notebooks.assert_called_once()
        self.view.show_notebooks.assert_called_once_with([])

    def test_execute_db_error(self):
        self.db.get_notebooks.side_effect = db.Error('Failed')

        command = commands.ListCommand(self.db, self.view)

        self.assertRaises(SystemExit, command.execute)
        self.db.get_notebooks.assert_called_once()
        self.view.show_notebooks.assert_not_called()
        self.view.show_error.assert_called_once_with('Failed')
