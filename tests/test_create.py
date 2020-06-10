import logging
import pathlib
import unittest
from unittest import mock

from pyfakefs import fake_filesystem_unittest as fakefs_unittest

from smth import controllers, db


class CreateControllerTestCase(unittest.TestCase):
    def setUp(self):
        logging.disable()

    def test_create_notebook(self):
        with mock.patch('smth.db.DB') as DB:
            db_mock = mock.MagicMock()
            db_mock.get_type_titles.return_value = []
            type_ = mock.MagicMock()
            type_.title = 'Type'
            db_mock.get_type_by_title.return_value = type_
            DB.return_value = db_mock

            with mock.patch('smth.view.View') as View:
                path = '/test/path.pdf'

                answers = {
                    'title': 'Notebook',
                    'type': 'Type',
                    'path': path,
                    'first_page_number': '1'
                }

                view = mock.MagicMock()
                view.ask_for_new_notebook_info.return_value = answers
                View.return_value = view

                with mock.patch('fpdf.FPDF') as FPDF:
                    pdf = mock.MagicMock()
                    FPDF.return_value = pdf

                    with fakefs_unittest.Patcher():
                        controller = controllers.CreateController('db_path')
                        controller.create_notebook()

                        db_mock.save_notebook.assert_called_once()
                        pdf.output.assert_called_once_with(path)
                        self.assertTrue(pathlib.Path(path).parent.exists)

    def test_create_notebook_path_not_pdf(self):
        with mock.patch('smth.db.DB') as DB:
            db_ = mock.MagicMock()
            db_.get_type_titles.return_value = []
            type_ = mock.MagicMock()
            type_.title = 'Type'
            db_.get_type_by_title.return_value = type_
            DB.return_value = db_

            with mock.patch('smth.view.View') as View:
                path = '/test/path'

                answers = {
                    'title': 'Notebook',
                    'type': 'Type',
                    'path': path,
                    'first_page_number': '1'
                }

                view = mock.MagicMock()
                view.ask_for_new_notebook_info.return_value = answers
                View.return_value = view

                with mock.patch('fpdf.FPDF') as FPDF:
                    pdf = mock.MagicMock()
                    FPDF.return_value = pdf

                    with fakefs_unittest.Patcher():
                        controller = controllers.CreateController('db_path')
                        controller.create_notebook()

                        db_.save_notebook.assert_called_once()
                        expected_path = str(pathlib.Path(path).joinpath(
                            'Notebook.pdf'))
                        pdf.output.assert_called_once_with(expected_path)
                        self.assertTrue(pathlib.Path(path).exists)

    def test_create_notebook_no_answers(self):
        with mock.patch('smth.db.DB') as DB:
            db_ = mock.MagicMock()
            db_.get_type_titles.return_value = []
            type_ = mock.MagicMock()
            type_.title = 'Type'
            db_.get_type_by_title.return_value = type_
            DB.return_value = db_

            with mock.patch('smth.view.View') as View:
                answers = None

                view = mock.MagicMock()
                view.ask_for_new_notebook_info.return_value = answers
                View.return_value = view

                with mock.patch('fpdf.FPDF') as FPDF:
                    pdf = mock.MagicMock()
                    FPDF.return_value = pdf

                    with fakefs_unittest.Patcher():
                        controller = controllers.CreateController('db_path')
                        controller.create_notebook()

                        db_.save_notebook.assert_not_called()
                        pdf.output.assert_not_called()

    def test_create_notebook_error(self):
        with mock.patch('smth.db.DB') as DB:
            db_ = mock.MagicMock()
            db_.get_type_titles.side_effect = db.Error('Fail')
            DB.return_value = db_

            with mock.patch('smth.view.View') as View:
                view = mock.MagicMock()
                View.return_value = view

                controller = controllers.CreateController('db_path')

                with mock.patch('sys.exit') as sys_exit:
                    controller.create_notebook()

                    db_.save_notebook.assert_not_called()
                    view.show_error.assert_called_once_with('Fail')
                    sys_exit.assert_called_once_with(1)
