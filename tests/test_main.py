import logging
import sys
from unittest import mock

from pyfakefs import fake_filesystem_unittest

from smth import config, db, main
from tests import testutils


class MainTestCase(fake_filesystem_unittest.TestCase):
    """Test program's entry point."""

    def setUp(self):
        self.setUpPyfakefs(modules_to_reload=[main, config])
        logging.disable()

        db_patcher = mock.patch('smth.db.DB')
        db_patcher.start().return_value = mock.MagicMock()
        self.addCleanup(db_patcher.stop)

    @mock.patch('smth.main')
    def test__main__(self, mock):
        from smth import __main__  # noqa: F401  # Cover __main__.py with tests

    def test_list_command(self):
        with mock.patch.object(sys, 'argv', ['', 'list']):
            with mock.patch('smth.commands.ListCommand') as Command:
                command = mock.MagicMock()
                Command.return_value = command
                main.main()
                command.execute.assert_called_once()

    def test_open_command(self):
        with mock.patch.object(sys, 'argv', ['', 'open']):
            with mock.patch('smth.commands.OpenCommand') as Command:
                command = mock.MagicMock()
                Command.return_value = command
                main.main()
                command.execute.assert_called_once()

    def test_scan_command(self):
        with mock.patch.object(sys, 'argv', ['', 'scan']):
            with mock.patch('smth.commands.ScanCommand') as Command:
                command = mock.MagicMock()
                Command.return_value = command
                main.main()
                command.execute.assert_called_once()

    def test_share_command(self):
        with mock.patch.object(sys, 'argv', ['', 'share']):
            with mock.patch('smth.commands.ShareCommand') as Command:
                command = mock.MagicMock()
                Command.return_value = command
                main.main()
                command.execute.assert_called_once()

    def test_share_command_pydrive_not_found(self):
        with mock.patch.object(sys, 'argv', ['', 'share']):
            with mock.patch('smth.commands.ShareCommand') as Command:
                with mock.patch('importlib.util.find_spec') as find_spec:
                    command = mock.MagicMock()
                    Command.return_value = command
                    find_spec.return_value = None
                    testutils.capture_stdout(main.main)
                    command.execute.assert_not_called()

    def test_types_command(self):
        with mock.patch.object(sys, 'argv', ['', 'types']):
            with mock.patch('smth.commands.TypesCommand') as Command:
                command = mock.MagicMock()
                Command.return_value = command
                main.main()
                command.execute.assert_called_once()

    def test_create_command(self):
        with mock.patch.object(sys, 'argv', ['', 'create']):
            with mock.patch('smth.commands.CreateCommand') as Command:
                command = mock.MagicMock()
                Command.return_value = command
                main.main()
                command.execute.assert_called_once()

    def test_delete_command(self):
        with mock.patch.object(sys, 'argv', ['', 'delete']):
            with mock.patch('smth.commands.DeleteCommand') as Command:
                command = mock.MagicMock()
                Command.return_value = command
                main.main()
                command.execute.assert_called_once()

    def test_update_command(self):
        with mock.patch.object(sys, 'argv', ['', 'update']):
            with mock.patch('smth.commands.UpdateCommand') as Command:
                command = mock.MagicMock()
                Command.return_value = command
                main.main()
                command.execute.assert_called_once()

    def test_upload_command(self):
        with mock.patch.object(sys, 'argv', ['', 'upload']):
            with mock.patch('smth.commands.UploadCommand') as Command:
                command = mock.MagicMock()
                Command.return_value = command
                main.main()
                command.execute.assert_called_once()

    def test_upload_command_pydrive_not_found(self):
        with mock.patch.object(sys, 'argv', ['', 'upload']):
            with mock.patch('smth.commands.UploadCommand') as Command:
                with mock.patch('importlib.util.find_spec') as find_spec:
                    command = mock.MagicMock()
                    Command.return_value = command
                    find_spec.return_value = None
                    testutils.capture_stdout(main.main)
                    command.execute.assert_not_called()

    @mock.patch.object(sys, 'argv', ['__main__.py', 'test'])
    def test_unknown_command(self):
        output = testutils.capture_stdout(main.main)
        for command in ['create', 'list', 'scan', 'types']:
            self.assertIn(command, output)

    @mock.patch.object(sys, 'argv', ['__main__.py'])
    def test_default_command(self):
        with mock.patch('smth.commands.ScanCommand') as Command:
            command = mock.MagicMock()
            Command.return_value = command
            main.main()
            command.execute.assert_called_once()

    def test_config_error(self):
        with mock.patch('smth.config.Config') as Config:
            Config.side_effect = config.Error('Fail')

            with mock.patch('smth.view.View') as View:
                view = mock.MagicMock()
                View.return_value = view

                self.assertRaises(SystemExit, main.main)
                view.show_error.assert_called_once_with('Fail.')

    def test_db_error(self):
        with mock.patch('smth.db.DB') as DB:
            DB.side_effect = db.Error('Fail')

            with mock.patch('smth.view.View') as View:
                view = mock.MagicMock()
                View.return_value = view

                self.assertRaises(SystemExit, main.main)
                view.show_error.assert_called_once_with('Fail.')
