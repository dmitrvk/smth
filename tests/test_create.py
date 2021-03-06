import argparse
import logging
import pathlib
from unittest import mock

from pyfakefs import fake_filesystem_unittest

from smth import commands, db


class CreateCommandTestCase(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        logging.disable()

        type_ = mock.MagicMock()
        type_.title = 'Type'

        self.db = mock.MagicMock()
        self.db.get_type_titles.return_value = ['A4']
        self.db.get_type_by_title.return_value = type_

        self.view = mock.MagicMock()

        self.pdf = mock.MagicMock()
        self.pdf.output = self.fs.create_file
        fpdf_patcher = mock.patch('fpdf.FPDF')
        fpdf_patcher.start().return_value = self.pdf
        self.addCleanup(fpdf_patcher.stop)

        self.args = argparse.ArgumentParser().parse_args([])

    def test_execute(self):
        path = pathlib.Path('/test/path.pdf')

        answers = {
            'title': 'notebook',
            'type': 'Type',
            'path': str(path),
            'first_page_number': 1
        }

        self.view.ask_for_new_notebook_info.return_value = answers

        commands.CreateCommand(self.db, self.view).execute(self.args)

        self.db.save_notebook.assert_called_once()
        self.assertTrue(path.exists())

    def test_execute_path_not_pdf(self):
        dir_path = pathlib.Path('/test/path')

        answers = {
            'title': 'notebook',
            'type': 'Type',
            'path': str(dir_path),
            'first_page_number': 1
        }

        self.view.ask_for_new_notebook_info.return_value = answers

        commands.CreateCommand(self.db, self.view).execute(self.args)

        self.db.save_notebook.assert_called_once()
        pdf_path = dir_path / 'notebook.pdf'
        self.assertTrue(pdf_path.exists())

    def test_execute_path_not_pdf_and_file_already_exists_in_dir(self):
        dir_path = pathlib.Path('/test/path')

        answers = {
            'title': 'notebook',
            'type': 'Type',
            'path': str(dir_path),
            'first_page_number': 1
        }

        self.fs.create_file(str(dir_path / 'notebook.pdf'))

        self.view.ask_for_new_notebook_info.return_value = answers

        command = commands.CreateCommand(self.db, self.view)
        self.assertRaises(SystemExit, command.execute, self.args)
        self.db.save_notebook.assert_not_called()
        self.view.show_error.assert_called()

    def test_execute_no_answers(self):
        self.view.ask_for_new_notebook_info.return_value = None
        self.pdf.output = mock.MagicMock()

        commands.CreateCommand(self.db, self.view).execute(self.args)

        self.db.save_notebook.assert_not_called()
        self.pdf.output.assert_not_called()

    def test_execute_no_types(self):
        self.db.get_type_titles.return_value = []

        with mock.patch(
                'smth.commands.types.TypesCommand') as command_constructor:
            command_ = mock.MagicMock()
            command_constructor.return_value = command_

            with self.assertRaises(SystemExit):
                commands.CreateCommand(self.db, self.view).execute(self.args)

        command_.execute.assert_called()
        self.db.save_notebook.assert_not_called()

    def test_execute_db_error(self):
        self.db.get_type_titles.side_effect = db.Error('Fail')

        command = commands.CreateCommand(self.db, self.view)

        self.assertRaises(SystemExit, command.execute, self.args)
        self.db.save_notebook.assert_not_called()
        self.view.show_error.assert_called_once_with('Fail')
