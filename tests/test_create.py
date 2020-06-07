import logging
import pathlib
import unittest
from unittest import mock

from pyfakefs import fake_filesystem_unittest as fakefs_unittest

from smth import controllers, db


class TestCreateController(unittest.TestCase):
    def setUp(self):
        logging.disable()

    def test_create_notebook(self):
        with mock.patch('smth.db.DB') as DB:
            db_mock = mock.MagicMock()
            db_mock.get_type_titles.return_value = []
            type_mock = mock.MagicMock()
            type_mock.title = 'Type'
            db_mock.get_type_by_title.return_value = type_mock
            DB.return_value = db_mock

            with mock.patch('smth.views.CreateView') as CreateView:
                path = '/test/path.pdf'

                answers = {
                    'title': 'Notebook',
                    'type': 'Type',
                    'path': path,
                    'first_page_number': '1'
                }

                view_mock = mock.MagicMock()
                view_mock.ask_for_new_notebook_info.return_value = answers
                CreateView.return_value = view_mock

                with mock.patch('fpdf.FPDF') as FPDF:
                    fpdf_mock = mock.MagicMock()
                    FPDF.return_value = fpdf_mock

                    with fakefs_unittest.Patcher() as fspatcher:
                        controller = controllers.CreateController('db_path')
                        controller.create_notebook()

                        db_mock.save_notebook.assert_called_once()
                        fpdf_mock.output.assert_called_once_with(path)
                        self.assertTrue(pathlib.Path(path).parent.exists)

    def test_create_notebook_path_not_pdf(self):
        with mock.patch('smth.db.DB') as DB:
            db_mock = mock.MagicMock()
            db_mock.get_type_titles.return_value = []
            type_mock = mock.MagicMock()
            type_mock.title = 'Type'
            db_mock.get_type_by_title.return_value = type_mock
            DB.return_value = db_mock

            with mock.patch('smth.views.CreateView') as CreateView:
                path = '/test/path'

                answers = {
                    'title': 'Notebook',
                    'type': 'Type',
                    'path': path,
                    'first_page_number': '1'
                }

                view_mock = mock.MagicMock()
                view_mock.ask_for_new_notebook_info.return_value = answers
                CreateView.return_value = view_mock

                with mock.patch('fpdf.FPDF') as FPDF:
                    fpdf_mock = mock.MagicMock()
                    FPDF.return_value = fpdf_mock

                    with fakefs_unittest.Patcher() as fspatcher:
                        controller = controllers.CreateController('db_path')
                        controller.create_notebook()

                        db_mock.save_notebook.assert_called_once()
                        expected_path = str(pathlib.Path(path).joinpath(
                            'Notebook.pdf'))
                        fpdf_mock.output.assert_called_once_with(expected_path)
                        self.assertTrue(pathlib.Path(path).exists)

    def test_create_notebook_no_answers(self):
        with mock.patch('smth.db.DB') as DB:
            db_mock = mock.MagicMock()
            db_mock.get_type_titles.return_value = []
            type_mock = mock.MagicMock()
            type_mock.title = 'Type'
            db_mock.get_type_by_title.return_value = type_mock
            DB.return_value = db_mock

            with mock.patch('smth.views.CreateView') as CreateView:
                answers = None

                view_mock = mock.MagicMock()
                view_mock.ask_for_new_notebook_info.return_value = answers
                CreateView.return_value = view_mock

                with mock.patch('fpdf.FPDF') as FPDF:
                    fpdf_mock = mock.MagicMock()
                    FPDF.return_value = fpdf_mock

                    with fakefs_unittest.Patcher() as fspatcher:
                        controller = controllers.CreateController('db_path')
                        controller.create_notebook()

                        db_mock.save_notebook.assert_not_called()
                        fpdf_mock.output.assert_not_called()

    def test_create_notebook_error(self):
        with mock.patch('smth.db.DB') as DB:
            db_mock = mock.MagicMock()
            db_mock.get_type_titles.side_effect = db.Error('Failed')
            DB.return_value = db_mock

            with mock.patch('smth.views.CreateView') as CreateView:
                create_view_mock = mock.MagicMock()
                CreateView.return_value = create_view_mock

                controller = controllers.CreateController('db_path')

                with mock.patch('sys.exit') as sys_exit:
                    controller.create_notebook()

                    db_mock.save_notebook.assert_not_called()
                    create_view_mock.show_error.assert_called_once_with('Failed')
                    sys_exit.assert_called_once_with(1)
