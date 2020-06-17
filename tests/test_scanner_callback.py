import pathlib
import unittest
from unittest import mock

from smth import commands


class ScannerCallbackTestCase(unittest.TestCase):
    def setUp(self):
        self.command = mock.MagicMock()
        self.db = mock.MagicMock()
        self.view = mock.MagicMock()
        self.conf = mock.MagicMock()

        self.callback = commands.ScanCommand.ScannerCallback(
            self.command, self.db, self.view, self.conf)

    def test_on_finish_scan_page(self):
        notebook = mock.MagicMock(**{
            'get_page_path.return_value': pathlib.Path('/test/path.pdf'),
        })

        image = mock.MagicMock()

        self.callback.on_finish_scan_page(notebook, 1, image)

        notebook.get_page_path.assert_called_once_with(1)
        image.save.assert_called_once_with('/test/path.pdf')
        self.view.show_info.assert_called_once()

    def test_on_finish(self):
        pass

    def test_on_error(self):
        self.assertTrue(hasattr(self.callback, 'on_error'))
        self.callback.on_error('Error')
