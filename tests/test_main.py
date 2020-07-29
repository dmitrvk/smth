import logging
import sys
from unittest import mock

from pyfakefs import fake_filesystem_unittest

from smth import config, const, db, main
from tests import testutils


class MainTestCase(fake_filesystem_unittest.TestCase):
    """Test program's entry point."""

    def setUp(self):
        self.setUpPyfakefs(modules_to_reload=[main, config, const])
        logging.disable()

        db_patcher = mock.patch('smth.db.DB')
        db_patcher.start().return_value = mock.MagicMock()
        self.addCleanup(db_patcher.stop)

        self.commands = [
            'create', 'delete', 'list', 'open', 'scan', 'share', 'types',
            'update', 'upload',
        ]

    @mock.patch('smth.main')
    def test__main__(self, mock):
        from smth import __main__  # noqa: F401  # Cover __main__.py with tests

    def test_commands_execution(self):
        for command in self.commands:
            with mock.patch.object(sys, 'argv', ['', command]):
                command_class = f'smth.commands.{command.capitalize()}Command'

                with mock.patch(command_class) as Command:
                    command = mock.MagicMock()
                    Command.return_value = command
                    main.main()
                    command.execute.assert_called_once()

    def test_pydrive_not_found(self):
        for command in ['share', 'upload']:
            with mock.patch.object(sys, 'argv', ['', command]):
                command_class = f'smth.commands.{command.capitalize()}Command'

                with mock.patch(command_class) as Command:
                    command = mock.MagicMock()
                    Command.return_value = command

                    with mock.patch('importlib.util.find_spec') as find_spec:
                        find_spec.return_value = None

                        testutils.capture_stdout(main.main)

                        command.execute.assert_not_called()

    def test_default_command(self):
        with mock.patch.object(sys, 'argv', ['__main__.py']):
            with mock.patch('smth.commands.ScanCommand') as Command:
                command = mock.MagicMock()
                Command.return_value = command
                main.main()
                command.execute.assert_called_once()

    def test_unknown_command(self):
        with mock.patch.object(sys, 'argv', ['__main__.py', 'test']):
            output = testutils.capture_stdout(main.main)
            for command in self.commands:
                self.assertIn(command, output)

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
