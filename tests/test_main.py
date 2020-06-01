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

    def test_scan_command(self):
        with mock.patch.object(sys, 'argv', ['', 'scan']):
            with mock.patch('smth.controllers.ScanController') as Controller:
                controller = mock.MagicMock()
                Controller.return_value = controller
                main.main()
                controller.scan_notebook.assert_called_once()

    def test_types_command(self):
        with mock.patch.object(sys, 'argv', ['', 'types']):
            with mock.patch('smth.controllers.TypesController') as Controller:
                controller_mock = mock.MagicMock()
                Controller.return_value = controller_mock
                main.main()
                controller_mock.show_types_list.assert_called_once()

    def test_create_command(self):
        with mock.patch.object(sys, 'argv', ['', 'create']):
            with mock.patch('smth.controllers.CreateController') as Controller:
                controller_mock = mock.MagicMock()
                Controller.return_value = controller_mock
                main.main()
                controller_mock.create_notebook.assert_called_once()

    @mock.patch.object(sys, 'argv', ['__main__.py'])
    def test_no_command(self):
        output = testutils.capture_stdout(main.main)
        for command in ['create', 'list', 'scan', 'types']:
            self.assertIn(command, output)

    @mock.patch.object(sys, 'argv', ['__main__.py', 'test'])
    def test_unknown_command(self):
        output = testutils.capture_stdout(main.main)
        for command in ['create', 'list', 'scan', 'types']:
            self.assertIn(command, output)

