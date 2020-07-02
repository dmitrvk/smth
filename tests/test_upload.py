import logging
import pathlib
from unittest import mock

from pyfakefs import fake_filesystem_unittest

from smth import commands, db, config, models


class UploadCommandTestCase(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs(modules_to_reload=[commands, config])
        self.fs.create_dir(str(config.Config.CONFIG_PATH.parent))
        self.fs.create_file(str(commands.UploadCommand.CLIENT_SECRETS_PATH))

        logging.disable()

        self.db = mock.MagicMock()
        self.view = mock.MagicMock()

        self.gauth = mock.MagicMock()
        gauth_patcher = mock.patch('pydrive.auth.GoogleAuth')
        gauth_patcher.start().return_value = self.gauth
        self.addCleanup(gauth_patcher.stop)

        self.drive = mock.MagicMock()
        drive_patcher = mock.patch('pydrive.drive.GoogleDrive')
        drive_patcher.start().return_value = self.drive
        self.addCleanup(drive_patcher.stop)

    def test_execute(self):
        self.db.get_notebook_titles.return_value = ['notebook']

        notebook = models.Notebook('notebook', None,
                                   pathlib.Path('/test/path.pdf'))
        self.db.get_notebook_by_title.return_value = notebook

        self.view.ask_for_notebook.return_value = 'notebook'

        commands.UploadCommand(self.db, self.view).execute()

        self.view.ask_for_notebook.assert_called_once()

    def test_execute_auth_no_credentials(self):
        with mock.patch(
                'smth.commands.UploadCommand.CREDENTIALS_PATH') as PATH:
            PATH.exists.return_value = False
            commands.UploadCommand(self.db, self.view).execute()

        self.gauth.CommandLineAuth.assert_called_once()
        self.gauth.SaveCredentialsFile.assert_called_once()

    def test_execute_auth_with_credentials(self):
        with mock.patch(
                'smth.commands.UploadCommand.CREDENTIALS_PATH') as PATH:
            PATH.exists.return_value = True
            commands.UploadCommand(self.db, self.view).execute()

        self.gauth.CommandLineAuth.assert_not_called()
        self.gauth.LoadCredentialsFile.assert_called_once()

    def test_execute_no_client_secrets(self):
        with mock.patch(
                'smth.commands.UploadCommand.CLIENT_SECRETS_PATH') as PATH:
            PATH.exists.return_value = True
            commands.UploadCommand(self.db, self.view).execute()

        path = str(commands.UploadCommand.CLIENT_SECRETS_PATH)
        self.assertTrue(self.fs.exists(path))

    def test_execute_smth_folder_not_exists(self):
        self.drive.ListFile.return_value = mock.MagicMock(**{
            'GetList.return_value': [],
        })

        commands.UploadCommand(self.db, self.view).execute()

        folder_metadata = {
            'title': 'smth',
            'mimeType': 'application/vnd.google-apps.folder',
        }

        expected_call = mock.call(folder_metadata)
        self.assertIn(expected_call, self.drive.CreateFile.mock_calls)

    def test_execute_smth_folder_exists(self):
        self.drive.ListFile.return_value = mock.MagicMock(**{
            'GetList.return_value': [{'id': 'folder_id', 'title': 'smth'}],
        })

        commands.UploadCommand(self.db, self.view).execute()

        folder_metadata = {
            'title': 'smth',
            'mimeType': 'application/vnd.google-apps.folder',
        }

        # Assert not called with metadata
        with self.assertRaises(AssertionError):
            self.drive.CreateFile.assert_called_with(folder_metadata)

    def test_execute_db_error(self):
        self.db.get_notebook_titles.side_effect = db.Error('Failed')

        command = commands.UploadCommand(self.db, self.view)

        self.assertRaises(SystemExit, command.execute)
        self.view.show_error.assert_called_once_with('Failed')

    def test_execute_no_notebooks(self):
        self.db.get_notebook_titles.return_value = []
        commands.UploadCommand(self.db, self.view).execute()
        self.view.ask_for_notebook.assert_not_called()

    def test_execute_pydrive_import_error(self):
        with mock.patch('builtins.__import__') as __import__:
            __import__.side_effect = ImportError

            with self.assertRaises(SystemExit):
                commands.UploadCommand(self.db, self.view).execute()

            self.view.ask_for_notebook.assert_not_called()
            self.view.show_error.assert_called_once()
