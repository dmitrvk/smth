import logging
import unittest
from unittest import mock

from smth import controllers, db


class TestListController(unittest.TestCase):
    def setUp(self):
        logging.disable()

    def test_show_notebooks_list(self):
        with mock.patch('smth.db.DB') as DB:
            db_mock = mock.MagicMock()
            db_mock.get_notebooks.return_value = []
            DB.return_value = db_mock

            with mock.patch('smth.views.ListView') as ListView:
                list_view_mock = mock.MagicMock()
                ListView.return_value = list_view_mock

                controller = controllers.ListController('db_path')
                controller.show_notebooks_list()

                db_mock.get_notebooks.assert_called_once()
                list_view_mock.show_notebooks.assert_called_once_with([])

    def test_show_notebooks_list_error(self):
        with mock.patch('smth.db.DB') as DB:
            db_mock = mock.MagicMock()
            db_mock.get_notebooks.side_effect = db.Error('Failed')
            DB.return_value = db_mock

            with mock.patch('smth.views.ListView') as ListView:
                list_view_mock = mock.MagicMock()
                ListView.return_value = list_view_mock

                controller = controllers.ListController('db_path')

                with mock.patch('sys.exit') as sys_exit:
                    controller.show_notebooks_list()

                    db_mock.get_notebooks.assert_called_once()
                    list_view_mock.show_notebooks.assert_not_called()
                    list_view_mock.show_error.assert_called_once_with('Failed')
                    sys_exit.assert_called_once_with(1)
