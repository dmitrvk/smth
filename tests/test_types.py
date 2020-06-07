import logging
import unittest
from unittest import mock

from smth import controllers, db


class TestTypesController(unittest.TestCase):
    def setUp(self):
        logging.disable()

    def test_show_types_list(self):
        with mock.patch('smth.db.DB') as DB:
            db_mock = mock.MagicMock()
            db_mock.get_types.return_value = []
            DB.return_value = db_mock

            with mock.patch('smth.views.TypesView') as TypesView:
                types_view_mock = mock.MagicMock()
                TypesView.return_value = types_view_mock

                controller = controllers.TypesController('db_path')
                controller.show_types_list()

                db_mock.get_types.assert_called_once()
                types_view_mock.show_types.assert_called_once_with([])

    def test_show_types_list_error(self):
        with mock.patch('smth.db.DB') as DB:
            db_mock = mock.MagicMock()
            db_mock.get_types.side_effect = db.Error('Fail')
            DB.return_value = db_mock

            with mock.patch('smth.views.TypesView') as TypesView:
                types_view_mock = mock.MagicMock()
                TypesView.return_value = types_view_mock

                controller = controllers.TypesController('db_path')

                with mock.patch('sys.exit') as sys_exit:
                    controller.show_types_list()

                    db_mock.get_types.assert_called_once()
                    types_view_mock.show_types.assert_not_called()
                    types_view_mock.show_error.assert_called_once_with('Fail')
                    sys_exit.assert_called_once_with(1)
