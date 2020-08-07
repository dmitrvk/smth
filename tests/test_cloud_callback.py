import pathlib
import unittest
from unittest import mock

from smth import commands


class UploadCallbackTestCase(unittest.TestCase):
    def setUp(self):
        self.command = mock.MagicMock()
        self.view = mock.MagicMock()

        self.callback = commands.UploadCommand.CloudCallback(
            self.command, self.view)

    def test_on_start_uploading_file(self):
        self.callback.on_start_uploading_file(pathlib.Path('/file.pdf'))
        self.view.show_info.assert_called()

    def test_on_confirm_overwrite_file(self):
        self.callback.on_confirm_overwrite_file('file.pdf')
        self.view.confirm.assert_called_once()

    def test_on_finish_uploading_file(self):
        self.callback.on_finish_uploading_file(pathlib.Path('/file.pdf'))
        self.view.show_info.assert_called()

    def test_on_create_smth_folder(self):
        self.callback.on_create_smth_folder()
        self.view.show_info.assert_called()

    def test_on_error(self):
        self.callback.on_error('message')
        self.command.exit_with_error.assert_called_once()


class SharingCallbackTestCase(unittest.TestCase):
    def setUp(self):
        self.command = mock.MagicMock()
        self.view = mock.MagicMock()

        self.callback = commands.ShareCommand.CloudCallback(
            self.command, self.view)

    def test_on_start_sharing_file(self):
        self.callback.on_start_sharing_file('file.pdf')

    def test_on_finish_sharing_file(self):
        self.callback.on_finish_sharing_file('file.pdf', 'https://someurl')
        self.view.show_info.assert_called()

    def test_on_finish_sharing_file_no_link(self):
        self.callback.on_finish_sharing_file('file.pdf', None)
        self.view.show_error.assert_called()

    def test_on_error(self):
        self.callback.on_error('message')
        self.command.exit_with_error.assert_called_once()
