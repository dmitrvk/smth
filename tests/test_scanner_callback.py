import pathlib
from unittest import mock

from pyfakefs import fake_filesystem_unittest

from smth import commands, models


class ScannerCallbackTestCase(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

        self.command = mock.MagicMock()
        self.db = mock.MagicMock()
        self.view = mock.MagicMock()
        self.conf = mock.MagicMock()

        self.callback = commands.ScanCommand.ScannerCallback(
            self.command, self.db, self.view, self.conf)

        self.pdf = mock.MagicMock()
        self.pdf.output = self.fs.create_file
        fpdf_patcher = mock.patch('fpdf.FPDF')
        fpdf_patcher.start().return_value = self.pdf
        self.addCleanup(fpdf_patcher.stop)

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
        type_ = models.NotebookType('', 160, 200)

        notebook = models.Notebook('', type_, pathlib.Path('/test/path.pdf'))
        notebook.total_pages = 3

        with mock.patch('importlib.util.find_spec') as find_spec:
            find_spec.return_value = None

            self.callback.on_finish(notebook)

        self.db.save_notebook.assert_called_once()
        self.assertEqual(self.pdf.add_page.call_count, 3)
        self.assertTrue(notebook.path.exists())

    def test_on_finish_paired_pages(self):
        type_ = models.NotebookType('', 160, 200)
        type_.pages_paired = True

        notebook = models.Notebook('', type_, pathlib.Path('/test/path.pdf'))
        notebook.total_pages = 4

        with mock.patch('importlib.util.find_spec') as find_spec:
            find_spec.return_value = None

            self.callback.on_finish(notebook)

        self.db.save_notebook.assert_called_once()
        self.assertEqual(self.pdf.add_page.call_count, 2)
        self.assertTrue(notebook.path.exists())

    def test_on_error(self):
        self.assertTrue(hasattr(self.callback, 'on_error'))
        self.callback.on_error('Error')

    def test_on_finish_upload_to_google_drive(self):
        type_ = models.NotebookType('', 160, 200)
        type_.pages_paired = True
        notebook = models.Notebook('test', type_, pathlib.Path('/path.pdf'))

        with mock.patch('importlib.util.find_spec') as find_spec:
            find_spec.return_value = 'spec'

            with mock.patch(
                    'smth.commands.upload.UploadCommand') as command_class:
                command = mock.MagicMock()
                command_class.return_value = command

                self.callback.on_finish(notebook)

                self.view.confirm.assert_called_once()
                command.execute.assert_called_once_with([notebook.title])
