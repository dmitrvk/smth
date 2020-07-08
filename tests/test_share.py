import logging
import pathlib
import unittest
from unittest import mock

from smth import commands, db, models


class ShareCommandTestCase(unittest.TestCase):
    def setUp(self):
        logging.disable()

        path = pathlib.Path('/test/path.pdf')
        self.notebook = models.Notebook('notebook', None, path)

        self.db = mock.MagicMock()
        self.db.get_notebook_titles.return_value = [self.notebook.title]
        self.db.get_notebook_by_title.return_value = self.notebook

        self.view = mock.MagicMock()
        self.view.ask_for_notebook.return_value = self.notebook.title

        self.cloud = mock.MagicMock()
        cloud_patcher = mock.patch('smth.cloud.Cloud')
        cloud_patcher.start().return_value = self.cloud
        self.addCleanup(cloud_patcher.stop)

        self.command = commands.ShareCommand(self.db, self.view)

    def test_execute_share_file(self):
        self.command.execute()

        self.view.ask_for_notebook.assert_called_once()
        self.cloud.share_file.assert_called_once()

    def test_execute_db_error_on_get_notebook_titles(self):
        self.db.get_notebook_titles.side_effect = db.Error('Failed')

        self.assertRaises(SystemExit, self.command.execute)

        self.view.ask_for_notebook.assert_not_called()
        self.cloud.share_file.assert_not_called()
        self.view.show_error.assert_called()

    def test_execute_db_error_on_get_notebook(self):
        self.db.get_notebook_by_title.side_effect = db.Error('Failed')

        self.assertRaises(SystemExit, self.command.execute)

        self.view.ask_for_notebook.assert_called_once()
        self.cloud.share_file.assert_not_called()
        self.view.show_error.assert_called()

    def test_execute_no_notebooks(self):
        self.db.get_notebook_titles.return_value = []

        self.command.execute()

        self.view.ask_for_notebook.assert_not_called()
        self.cloud.share_file.assert_not_called()
