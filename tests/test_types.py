import logging
import unittest
from unittest import mock

from smth import controllers, db


class TypesControllerTestCase(unittest.TestCase):
    def setUp(self):
        logging.disable()

    def test_show_types_list(self):
        with mock.patch('smth.db.DB') as DB:
            db_ = mock.MagicMock()
            db_.get_types.return_value = []
            DB.return_value = db_

            with mock.patch('smth.view.View') as View:
                view = mock.MagicMock()
                View.return_value = view

                controller = controllers.TypesController('db_path')
                controller.show_types_list()

                db_.get_types.assert_called_once()
                view.show_types.assert_called_once_with([])

    def test_show_types_list_error(self):
        with mock.patch('smth.db.DB') as DB:
            db_ = mock.MagicMock()
            db_.get_types.side_effect = db.Error('Fail')
            DB.return_value = db_

            with mock.patch('smth.view.View') as View:
                view = mock.MagicMock()
                View.return_value = view

                controller = controllers.TypesController('db_path')

                with mock.patch('sys.exit') as sys_exit:
                    controller.show_types_list()

                    db_.get_types.assert_called_once()
                    view.show_types.assert_not_called()
                    view.show_error.assert_called_once_with('Fail')
                    sys_exit.assert_called_once_with(1)
