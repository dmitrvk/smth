import logging
import unittest
from unittest import mock

import _sane
import sane

from smth import controllers, db


class ScanControllerTestCase(unittest.TestCase):
    def setUp(self):
        logging.disable()

        self.config = mock.MagicMock()
        self.config.scanner_device = None
        self.config.scanner_delay = 0

        sane.init = mock.MagicMock()
        sane.get_devices = mock.MagicMock(return_value=[])
        sane.open = mock.MagicMock()

    def test_scan(self):
        with mock.patch.object(db, 'DB') as DB:
            notebook = mock.MagicMock()
            notebook.title = 'Notebook'
            notebook.path = '/test/path.pdf'
            notebook.total_pages = 0

            db_ = mock.MagicMock()
            db_.get_notebook_titles.return_value = ['Notebook']
            db_.get_notebook_by_title.return_value = notebook
            DB.return_value = db_

            with mock.patch('fpdf.FPDF') as FPDF:
                pdf = mock.MagicMock()
                FPDF.return_value = pdf

                with mock.patch('smth.view.View') as View:
                    scan_prefs = {
                        'device': 'dev',
                        'notebook': 'Notebook',
                        'append': '3'
                    }

                    view = mock.MagicMock()
                    view.ask_for_scan_prefs.return_value = scan_prefs
                    View.return_value = view

                    image = mock.MagicMock()
                    image.size = (100, 200)
                    scanner = mock.MagicMock()
                    scanner.scan.return_value = image
                    sane.open.return_value = scanner

                    controllers.ScanController(
                        [], '', self.config).scan_notebook()

                    db_.save_notebook.assert_called_once()
                    scanner.close.assert_called_once()
                    self.assertEqual(image.save.call_count, 3)
                    self.assertEqual(pdf.add_page.call_count, 3)
                    self.assertEqual(pdf.image.call_count, 3)

    def test_scan_device_set(self):
        conf = mock.MagicMock()
        conf.scanner_device = 'device'

        with mock.patch.object(db, 'DB') as DB:
            DB.return_value = mock.MagicMock()

            with mock.patch('smth.view.View') as View:
                View.return_value = mock.MagicMock()

                controllers.ScanController([], '', conf).scan_notebook()

                sane.get_devices.assert_not_called()

    def test_scan_wrong_device_set(self):
        conf = mock.MagicMock()
        conf.scanner_device = 'device'

        sane.open = mock.MagicMock(side_effect=_sane.error)

        with mock.patch.object(db, 'DB') as DB:
            db_ = mock.MagicMock()
            DB.return_value = db_

            with mock.patch('smth.view.View') as View:
                view = mock.MagicMock()
                View.return_value = view

                controller = controllers.ScanController([], '', conf)

                self.assertRaises(SystemExit, controller.scan_notebook)
                db_.save_notebook.assert_not_called()
                view.show_error.assert_called_once()

    def test_scan_keyboard_interrupt_when_searching_for_devices(self):
        sane.get_devices.side_effect = KeyboardInterrupt

        with mock.patch.object(db, 'DB') as DB:
            db_ = mock.MagicMock()
            DB.return_value = db_

            with mock.patch('smth.view.View') as View:
                view = mock.MagicMock()
                View.return_value = view

                controllers.ScanController([], '', self.config).scan_notebook()

                view.ask_for_scan_prefs.assert_not_called()
                sane.open.assert_not_called()
                db_.save_notebook.assert_not_called()

    def test_scan_no_scan_prefs(self):
        with mock.patch('smth.view.View') as View:
            view = mock.MagicMock()
            view.ask_for_scan_prefs.return_value = None
            View.return_value = view

            with mock.patch.object(db, 'DB') as DB:
                db_ = mock.MagicMock()
                db_.get_notebook_titles.return_value = ['Notebook']
                DB.return_value = db_

                controllers.ScanController([], '', self.config).scan_notebook()

                sane.open.assert_not_called()
                db_.save_notebook.assert_not_called()

    def test_scan_no_new_pages(self):
        with mock.patch('smth.view.View') as View:
            scan_prefs = {
                'device': 'dev',
                'notebook': 'Notebook',
                'append': ''
            }

            view = mock.MagicMock()
            view.ask_for_scan_prefs.return_value = scan_prefs
            View.return_value = view

            with mock.patch.object(db, 'DB') as DB:
                db_ = mock.MagicMock()
                db_.get_notebook_titles.return_value = ['Notebook']
                DB.return_value = db_

                controllers.ScanController([], '', self.config).scan_notebook()

                sane.open.assert_not_called()
                db_.save_notebook.assert_not_called()

    def test_scan_cannot_open_device(self):
        sane.open = mock.MagicMock(side_effect=_sane.error)

        with mock.patch.object(db, 'DB') as DB:
            db_ = mock.MagicMock()
            DB.return_value = db_

            with mock.patch('smth.view.View') as View:
                scan_prefs = {
                    'device': 'device',
                    'notebook': 'Notebook',
                    'append': '1'
                }

                view = mock.MagicMock()
                view.ask_for_scan_prefs.return_value = scan_prefs
                View.return_value = view

                controller = controllers.ScanController([], '', self.config)

                self.assertRaises(SystemExit, controller.scan_notebook)
                db_.save_notebook.assert_not_called()
                view.show_error.assert_called_once()

    def test_scan_db_error(self):
        with mock.patch.object(db, 'DB') as DB:
            db_ = mock.MagicMock()
            db_.get_notebook_titles.side_effect = db.Error
            DB.return_value = db_

            with mock.patch('smth.view.View') as View:
                scan_prefs = {
                    'device': 'dev',
                    'notebook': 'Notebook',
                    'append': ''
                }

                view = mock.MagicMock()
                view.ask_for_scan_prefs.return_value = scan_prefs
                View.return_value = view

                controller = controllers.ScanController([], '', self.config)

                self.assertRaises(SystemExit, controller.scan_notebook)

                view.ask_for_scan_prefs.assert_not_called()
                sane.open.assert_not_called()
                db_.save_notebook.assert_not_called()

    def test_scan_keyboard_interrupt_during_scanning(self):
        with mock.patch('smth.view.View') as View:
            scan_prefs = {
                'device': 'dev',
                'notebook': 'Notebook',
                'append': '3'
            }

            view = mock.MagicMock()
            view.ask_for_scan_prefs.return_value = scan_prefs
            View.return_value = view

            scanner = mock.MagicMock()
            scanner.scan.side_effect = KeyboardInterrupt
            sane.open.return_value = scanner

            with mock.patch.object(db, 'DB') as DB:
                notebook = mock.MagicMock()
                notebook.title = 'Notebook'
                notebook.path = '/test/path.pdf'
                notebook.total_pages = 0

                db_ = mock.MagicMock()
                db_.get_notebook_titles.return_value = ['Notebook']
                db_.get_notebook_by_title.return_value = notebook
                DB.return_value = db_

                controllers.ScanController([], '', self.config).scan_notebook()

                scanner.close.assert_called_once()
                db_.save_notebook.assert_not_called()

    def test_scan_sane_error_during_scanning(self):
        scanner_mock = mock.MagicMock()
        scanner_mock.scan.side_effect = _sane.error
        sane.open.return_value = scanner_mock

        with mock.patch.object(db, 'DB') as DB:
            db_ = mock.MagicMock()
            DB.return_value = db_

            with mock.patch('smth.view.View') as View:
                scan_prefs = {
                    'device': 'device',
                    'notebook': 'Notebook',
                    'append': '1'
                }

                view = mock.MagicMock()
                view.ask_for_scan_prefs.return_value = scan_prefs
                View.return_value = view

                controller = controllers.ScanController([], '', self.config)

                self.assertRaises(SystemExit, controller.scan_notebook)
                db_.save_notebook.assert_not_called()
                view.show_error.assert_called_once()

    def test_scan_no_notebooks(self):
        with mock.patch.object(db, 'DB') as DB:
            db_ = mock.MagicMock()
            db_.get_notebook_titles.return_value = []
            DB.return_value = db_

            with mock.patch('smth.view.View') as View:
                view = mock.MagicMock()
                View.return_value = view

                controllers.ScanController([], '', self.config).scan_notebook()

                view.ask_for_scan_prefs.assert_not_called
                sane.init.assert_not_called()
