import httplib2
import pathlib
import shutil
import unittest
from unittest import mock

from smth import cloud


class CloudTestCase(unittest.TestCase):
    def setUp(self):
        self.callback = mock.MagicMock()

        self.path = pathlib.Path('/test/notebook.pdf')

        self.test_dir_path = pathlib.Path('test_config')
        self.test_dir_path.mkdir(exist_ok=True)

        cloud.Cloud.SECRETS_PATH = self.test_dir_path / 'client_secrets.json'
        cloud.Cloud.CREDENTIALS_PATH = self.test_dir_path / 'credentials.json'

        self.gauth = mock.MagicMock()
        gauth_patcher = mock.patch('pydrive.auth.GoogleAuth')
        gauth_patcher.start().return_value = self.gauth
        self.addCleanup(gauth_patcher.stop)

        self.gdrive = mock.MagicMock()
        self.gdrive.ListFile.return_value = mock.MagicMock(**{
            'GetList.return_value': [{'id': 'folder_id', 'title': 'smth'}],
        })
        drive_patcher = mock.patch('pydrive.drive.GoogleDrive')
        drive_patcher.start().return_value = self.gdrive
        self.addCleanup(drive_patcher.stop)

        # file['title'] should return filename
        self.file = mock.MagicMock()
        self.file.__getitem__.return_value = self.path.name

    def test_auth(self):
        cloud.Cloud(self.callback)

        self.gauth.CommandLineAuth.assert_called_once()

        path = cloud.Cloud.CREDENTIALS_PATH
        self.gauth.SaveCredentialsFile.assert_called_once_with(str(path))

    def test_auth_credentials_exist(self):
        cloud.Cloud.CREDENTIALS_PATH.touch()

        cloud.Cloud(self.callback)

        self.gauth.LoadCredentialsFile.assert_called_once()
        self.gauth.CommandLineAuth.assert_not_called()

    def test_auth_server_not_found(self):
        self.gauth.CommandLineAuth.side_effect = httplib2.ServerNotFoundError

        cloud.Cloud(self.callback)

        self.gauth.SaveCredentialsFile.assert_not_called()
        self.callback.on_error.assert_called_once()

    def test_auth_keyboard_interrupt(self):
        self.gauth.CommandLineAuth.side_effect = KeyboardInterrupt

        cloud.Cloud(self.callback)

        self.gauth.SaveCredentialsFile.assert_not_called()
        self.callback.on_error.assert_called_once()

    def test_upload_new_file(self):
        self.gdrive.CreateFile.return_value = self.file

        cloud.Cloud(self.callback).upload_file(self.path)

        self.file.SetContentFile.assert_called_once_with(str(self.path))
        self.file.Upload.assert_called_once()
        self.callback.on_finish_uploading_file.assert_called_once()

    def test_upload_existing_file(self):
        self.gdrive.ListFile.return_value = mock.MagicMock(**{
            'GetList.return_value': [
                {'id': 'folder_id', 'title': 'smth'},
                self.file,
            ],
        })

        self.callback.on_confirm_override_file.return_value = True

        cloud.Cloud(self.callback).upload_file(self.path)

        self.file.SetContentFile.assert_called_once_with(str(self.path))
        self.file.Upload.assert_called_once()
        self.callback.on_finish_uploading_file.assert_called_once()

    def test_upload_when_smth_folder_doesnt_exist(self):
        self.gdrive.ListFile.return_value = mock.MagicMock(**{
            'GetList.return_value': [],
        })

        cloud.Cloud(self.callback).upload_file(self.path)

        folder_metadata = {
            'title': 'smth',
            'mimeType': 'application/vnd.google-apps.folder',
        }

        expected_call = mock.call(folder_metadata)
        self.assertIn(expected_call, self.gdrive.CreateFile.mock_calls)

    def test_errors_when_creating_smth_folder(self):
        self.gdrive.ListFile.return_value = mock.MagicMock(**{
            'GetList.return_value': [],
        })

        errors = (httplib2.ServerNotFoundError, KeyboardInterrupt)

        folder_metadata = {
            'title': 'smth',
            'mimeType': 'application/vnd.google-apps.folder',
        }

        for error in errors:
            def mock_upload():
                expected_call = mock.call(folder_metadata)

                if self.gdrive.CreateFile.mock_calls.pop() == expected_call:
                    raise error

            self.file.Upload = mock_upload
            self.gdrive.CreateFile.return_value = self.file

            cloud.Cloud(self.callback).upload_file(self.path)

        self.assertEqual(self.callback.on_error.call_count, 2)

    def test_upload_errors(self):
        self.gdrive.CreateFile.return_value = self.file

        upload_errors = (
            OSError, httplib2.ServerNotFoundError, KeyboardInterrupt)

        for error in upload_errors:
            self.file.Upload.side_effect = error
            cloud.Cloud(self.callback).upload_file(self.path)

        self.assertEqual(self.callback.on_error.call_count, 3)

    def test_get_list_errors(self):
        get_list_errors = (httplib2.ServerNotFoundError, KeyboardInterrupt)

        for error in get_list_errors:
            self.gdrive.ListFile.return_value = mock.MagicMock(**{
                'GetList.side_effect': error,
            })

            cloud.Cloud(self.callback).upload_file(self.path)

        self.assertEqual(self.callback.on_error.call_count, 4)

    def test_share_file(self):
        self.gdrive.ListFile.return_value = mock.MagicMock(**{
            'GetList.return_value': [
                {'id': 'folder_id', 'title': 'smth'},
                self.file,
            ],
        })

        cloud.Cloud(self.callback).share_file(self.path.name)

        self.file.InsertPermission.assert_called_once()

    def test_share_file_errors(self):
        self.gdrive.ListFile.return_value = mock.MagicMock(**{
            'GetList.return_value': [
                {'id': 'folder_id', 'title': 'smth'},
                self.file,
            ],
        })

        errors = (httplib2.ServerNotFoundError, KeyboardInterrupt)

        for error in errors:
            self.file.InsertPermission.side_effect = error
            cloud.Cloud(self.callback).share_file(self.path.name)

        self.assertEqual(self.file.InsertPermission.call_count, 2)

    def test_share_not_uploaded_file(self):
        cloud.Cloud(self.callback).share_file(self.path.name)

        self.file.InsertPermission.assert_not_called()
        self.callback.on_error.assert_called_once()

    def tearDown(self):
        shutil.rmtree(str(self.test_dir_path))
