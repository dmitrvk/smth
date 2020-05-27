import sys
import unittest
from unittest import mock

from pyfakefs import fake_filesystem_unittest

from smth import main
from tests import testutils


class TestMain(fake_filesystem_unittest.TestCase):
    """Test program's entry point."""

    def setUp(self):
        self.setUpPyfakefs()
        self.fs.create_file(main.LOG_FILE)

    @mock.patch('smth.main')
    def test__main__(self, mock):
        from smth import __main__

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

