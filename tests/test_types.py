import logging
import unittest
from unittest import mock

from smth import commands, db


class TypesControllerTestCase(unittest.TestCase):
    def setUp(self):
        logging.disable()

        self.db = mock.MagicMock()
        self.view = mock.MagicMock()

    def test_execute(self):
        self.db.get_types.return_value = []

        commands.TypesCommand(self.db, self.view).execute()

        self.db.get_types.assert_called_once()
        self.view.show_types.assert_called_once_with([])

    def test_execute_db_error(self):
        self.db.get_types.side_effect = db.Error('Fail')

        command = commands.TypesCommand(self.db, self.view)

        self.assertRaises(SystemExit, command.execute)
        self.db.get_types.assert_called_once()
        self.view.show_types.assert_not_called()
        self.view.show_error.assert_called_once_with('Fail')
