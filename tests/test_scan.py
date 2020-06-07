import logging
import os
import sys
import unittest
from unittest import mock

import fpdf
import sane
from pyfakefs import fake_filesystem_unittest as fakefs_unittest

from smth import db
from smth import controllers
from smth import models
from smth import views
from tests import testutils


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
            notebook_mock = mock.MagicMock()
            notebook_mock.title = 'Notebook'
            notebook_mock.path = '/test/path.pdf'
            notebook_mock.total_pages = 0

            db_mock = mock.MagicMock()
            db_mock.get_notebook_titles.return_value = ['Notebook']
            db_mock.get_notebook_by_title.return_value = notebook_mock
            DB.return_value = db_mock

            with mock.patch.object(fpdf, 'FPDF') as FPDF:
                pdf_mock = mock.MagicMock()
                FPDF.return_value = pdf_mock

                with mock.patch('smth.views.ScanView') as ScanView:
                    scan_prefs = {
                        'device': 'dev',
                        'notebook': 'Notebook',
                        'append': '3'
                    }

                    view_mock = mock.MagicMock()
                    view_mock.ask_for_scan_prefs.return_value = scan_prefs
                    ScanView.return_value = view_mock

                    image_mock = mock.MagicMock()
                    image_mock.size = (100, 200)
                    scanner_mock = mock.MagicMock()
                    scanner_mock.scan.return_value = image_mock
                    sane.open.return_value = scanner_mock

                    controllers.ScanController(
                        [], '', self.config).scan_notebook()

                    db_mock.save_notebook.assert_called_once()
                    scanner_mock.close.assert_called_once()
                    self.assertEqual(image_mock.save.call_count, 3)
                    self.assertEqual(pdf_mock.add_page.call_count, 3)
                    self.assertEqual(pdf_mock.image.call_count, 3)

    def test_scan_keyboard_interrupt_when_searching_for_devices(self):
        sane.get_devices.side_effect = KeyboardInterrupt

        with mock.patch.object(db, 'DB') as DB:
            db_ = mock.MagicMock()
            DB.return_value = db_

            with mock.patch('smth.views.ScanView') as ScanView:
                view = mock.MagicMock()
                ScanView.return_value = view

                controllers.ScanController([], '', self.config).scan_notebook()

                view.ask_for_scan_prefs.assert_not_called()
                sane.open.assert_not_called()
                db_.save_notebook.assert_not_called()

    def test_scan_no_scan_prefs(self):
        with mock.patch('smth.views.ScanView') as ScanView:
            view = mock.MagicMock()
            view.ask_for_scan_prefs.return_value = None
            ScanView.return_value = view

            with mock.patch.object(db, 'DB') as DB:
                db_ = mock.MagicMock()
                db_.get_notebook_titles.return_value = ['Notebook']
                DB.return_value = db_

                controllers.ScanController([], '', self.config).scan_notebook()

                sane.open.assert_not_called()
                db_.save_notebook.assert_not_called()

    def test_scan_no_new_pages(self):
        with mock.patch('smth.views.ScanView') as ScanView:
            scan_prefs = {
                'device': 'dev',
                'notebook': 'Notebook',
                'append': ''
            }

            view = mock.MagicMock()
            view.ask_for_scan_prefs.return_value = scan_prefs
            ScanView.return_value = view

            with mock.patch.object(db, 'DB') as DB:
                db_ = mock.MagicMock()
                db_.get_notebook_titles.return_value = ['Notebook']
                DB.return_value = db_

                controllers.ScanController([], '', self.config).scan_notebook()

                sane.open.assert_not_called()
                db_.save_notebook.assert_not_called()

    def test_scan_db_error(self):
        with mock.patch.object(db, 'DB') as DB:
            db_ = mock.MagicMock()
            db_.get_notebook_titles.side_effect = db.Error
            DB.return_value = db_

            with mock.patch('smth.views.ScanView') as ScanView:
                scan_prefs = {
                    'device': 'dev',
                    'notebook': 'Notebook',
                    'append': ''
                }

                view = mock.MagicMock()
                view.ask_for_scan_prefs.return_value = scan_prefs
                ScanView.return_value = view

                controller = controllers.ScanController([], '', self.config)

                self.assertRaises(SystemExit, controller.scan_notebook)

                view.ask_for_scan_prefs.assert_not_called()
                sane.open.assert_not_called()
                db_.save_notebook.assert_not_called()

    def test_scan_keyboard_interrupt_during_scanning(self):
        with mock.patch('smth.views.ScanView') as ScanView:
            scan_prefs = {
                'device': 'dev',
                'notebook': 'Notebook',
                'append': '3'
            }

            view = mock.MagicMock()
            view.ask_for_scan_prefs.return_value = scan_prefs
            ScanView.return_value = view

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

    def test_scan_no_notebooks(self):
        with mock.patch.object(db, 'DB') as DB:
            db_ = mock.MagicMock()
            db_.get_notebook_titles.return_value = []
            DB.return_value = db_

            with mock.patch('smth.views.ScanView') as ScanView:
                view = mock.MagicMock()
                ScanView.return_value = view

                controllers.ScanController([], '', self.config).scan_notebook()

                view.ask_for_scan_prefs.assert_not_called
                sane.init.assert_not_called()

