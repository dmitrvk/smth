import logging
import pathlib
from unittest import mock

from pyfakefs import fake_filesystem_unittest

from smth import commands, db, models


class UploadCommandTestCase(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs(modules_to_reload=[commands])
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

    def test_execute_upload_notebook_chosen_by_user(self):
        commands.UploadCommand(self.db, self.view).execute()
        self.view.ask_for_notebook.assert_called_once()
        self.cloud.upload_file.assert_called_once_with(self.notebook.path)

    def test_execute_upload_notebook_provided_with_arg(self):
        args = [self.notebook.title]
        commands.UploadCommand(self.db, self.view).execute(args)
        self.view.ask_for_notebook.assert_not_called()
        self.cloud.upload_file.assert_called_once_with(self.notebook.path)

    def test_execute_db_error(self):
        self.db.get_notebook_titles.side_effect = db.Error('Failed')
        command = commands.UploadCommand(self.db, self.view)
        self.assertRaises(SystemExit, command.execute)
        self.cloud.upload_file.assert_not_called()
        self.view.show_error.assert_called_once_with('Failed')

    def test_execute_no_notebooks(self):
        self.db.get_notebook_titles.return_value = []
        commands.UploadCommand(self.db, self.view).execute()
        self.view.ask_for_notebook.assert_not_called()
        self.cloud.upload_file.assert_not_called()
