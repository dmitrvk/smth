import sys
import unittest
from unittest import mock

from pyfakefs import fake_filesystem_unittest

from smth import controllers
from smth import main
from tests import testutils


class TestMain(fake_filesystem_unittest.TestCase):
    """Test program's entry point."""

    def setUp(self):
        self.setUpPyfakefs()

    @mock.patch('smth.main')
    def test__main__(self, mock):
        from smth import __main__

    def test_list_command(self):
        with mock.patch.object(sys, 'argv', ['', 'list']):
            with mock.patch('smth.controllers.ListController') as Controller:
                controller_mock = mock.MagicMock()
                Controller.return_value = controller_mock
                main.main()
                controller_mock.show_notebooks_list.assert_called_once()

    def test_types_command(self):
        with mock.patch.object(sys, 'argv', ['', 'types']):
            with mock.patch('smth.controllers.TypesController') as Controller:
                controller_mock = mock.MagicMock()
                Controller.return_value = controller_mock
                main.main()
                controller_mock.show_types_list.assert_called_once()

    @mock.patch.object(sys, 'argv', ['__main__.py'])
    def test_no_command(self):
        with mock.patch('smth.backup_system.db.DB'):
            output = testutils.capture_stdout(main.main)
            for command in ['create', 'list', 'scan', 'types']:
                self.assertIn(command, output)

    @mock.patch.object(sys, 'argv', ['__main__.py', 'test'])
    def test_unknown_command(self):
        with mock.patch('smth.backup_system.db.DB'):
            output = testutils.capture_stdout(main.main)
            for command in ['create', 'list', 'scan', 'types']:
                self.assertIn(command, output)

    @mock.patch('smth.backup_system.BackupSystem')
    @mock.patch.object(sys, 'argv', ['__main__.py', 'test'])
    def test_available_command(self, backup_system_mock):
        def test_command():
            print('Test Output')
        backup_system = backup_system_mock.return_value
        backup_system.test.side_effect = test_command
        output = testutils.capture_stdout(main.main)
        self.assertEqual(output, 'Test Output\n')

