import logging
import os
import sys
import unittest
from unittest import mock

import fpdf
from pyfakefs import fake_filesystem_unittest as fakefs_unittest

from smth import backup_system
from smth import db
from smth import controllers
from smth import models
from smth import views
from tests import testutils


class TestBackupSystem(unittest.TestCase):
    DB_PATH = 'smth-test.db'

    def setUp(self):
        logging.disable()

        self.view = mock.MagicMock()
        self.view.show_notebooks = print
        self.view.show_types = print

    @mock.patch.object(db, 'DB', side_effect=db.Error)
    def test_init_error(self, db_mock):
        with mock.patch.object(sys, 'exit') as sys_exit:
            backup_system.BackupSystem(self.view, self.DB_PATH)
            sys_exit.assert_called_once()

    @mock.patch.object(db, 'DB')
    def test_create(self, db_constructor_mock):
        answers = {
            'title': 'Notebook',
            'type': 'Type 1',
            'path': '/test/path.pdf',
            'first_page_number': '1'
        }

        self.view.ask_for_new_notebook_info.return_value = answers

        db_mock = mock.MagicMock()
        db_mock.get_notebook_titles.return_value=['Notebook']
        type_mock = mock.MagicMock()
        type_mock.title = 'Type 1'
        db_mock.get_type_by_title.return_value = type_mock

        db_constructor_mock.return_value = db_mock

        backup_system_ = backup_system.BackupSystem(self.view, self.DB_PATH)

        with mock.patch.object(fpdf, 'FPDF') as fpdf_constructor_mock:
            with fakefs_unittest.Patcher():
                fpdf_mock = mock.MagicMock()
                fpdf_constructor_mock.return_value = fpdf_mock
                backup_system_.create()
                db_mock.save_notebook.assert_called_once()
                fpdf_mock.output.assert_called_once()

    @mock.patch.object(db, 'DB')
    def test_create_path_not_pdf(self, db_constructor_mock):
        answers = {
            'title': 'Notebook',
            'type': 'Type 1',
            'path': '/test/path/',
            'first_page_number': '1'
        }

        self.view.ask_for_new_notebook_info.return_value = answers

        db_mock = mock.MagicMock()
        db_mock.get_notebook_titles.return_value=['Notebook']
        type_mock = mock.MagicMock()
        type_mock.title = 'Type 1'
        db_mock.get_type_by_title.return_value = type_mock

        db_constructor_mock.return_value = db_mock

        backup_system_ = backup_system.BackupSystem(self.view, self.DB_PATH)

        with mock.patch.object(fpdf, 'FPDF') as fpdf_constructor_mock:
            with fakefs_unittest.Patcher():
                fpdf_mock = mock.MagicMock()
                fpdf_constructor_mock.return_value = fpdf_mock
                backup_system_.create()
                db_mock.save_notebook.assert_called_once()
                fpdf_mock.output.assert_called_once()

    @mock.patch.object(db, 'DB')
    def test_create_no_answers(self, db_constructor_mock):
        self.view.ask_for_new_notebook_info.return_value = None

        db_mock = mock.MagicMock()
        db_mock.get_notebook_titles.return_value = ['Notebook']
        type_mock = mock.MagicMock()
        type_mock.title = 'Type 1'
        db_mock.get_type_by_title.return_value = type_mock

        db_constructor_mock.return_value = db_mock

        backup_system_ = backup_system.BackupSystem(self.view, self.DB_PATH)

        with mock.patch.object(fpdf, 'FPDF') as fpdf_constructor_mock:
            with fakefs_unittest.Patcher():
                fpdf_mock = mock.MagicMock()
                fpdf_constructor_mock.return_value = fpdf_mock
                backup_system_.create()
                db_mock.save_notebook.assert_not_called()
                fpdf_mock.output.assert_not_called()

    @mock.patch.object(db, 'DB')
    def test_create_error(self, db_constructor_mock):
        db_mock = mock.MagicMock()
        db_mock.get_type_titles.side_effect = db.Error

        db_constructor_mock.return_value = db_mock

        backup_system_ = backup_system.BackupSystem(self.view, self.DB_PATH)

        with mock.patch.object(sys, 'exit') as sys_exit:
            backup_system_.create()
            sys_exit.assert_called_once()

    def test_scan(self):
        scan_prefs = {
            'device': 'dev',
            'notebook': 'Notebook',
            'append': '3'
        }

        self.view.ask_for_scan_prefs.return_value = scan_prefs

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

                with mock.patch('smth.backup_system.sane') as sane_mock:
                    image_mock = mock.MagicMock()
                    image_mock.size = (100, 200)

                    scanner_mock = mock.MagicMock()
                    scanner_mock.scan.return_value = image_mock

                    sane_mock.get_devices.return_value = []
                    sane_mock.open.return_value = scanner_mock

                    backup_system.BackupSystem(self.view, self.DB_PATH).scan()

                    db_mock.save_notebook.assert_called_once()
                    scanner_mock.close.assert_called_once()
                    self.assertEqual(image_mock.save.call_count, 3)
                    self.assertEqual(pdf_mock.add_page.call_count, 3)
                    self.assertEqual(pdf_mock.image.call_count, 3)

    def test_scan_keyboard_interrupt_when_searching_for_devices(self):
        with mock.patch('smth.backup_system.sane') as sane_mock:
            sane_mock.get_devices.side_effect = KeyboardInterrupt

            with mock.patch.object(db, 'DB') as DB:
                db_mock = mock.MagicMock()
                DB.return_value = db_mock

                backup_system.BackupSystem(self.view, self.DB_PATH).scan()

                self.view.ask_for_scan_prefs.assert_not_called()
                sane_mock.open.assert_not_called()
                db_mock.save_notebook.assert_not_called()

    def test_scan_no_scan_prefs(self):
        self.view.ask_for_scan_prefs.return_value = None

        with mock.patch('smth.backup_system.sane') as sane_mock:
            sane_mock.get_devices.return_value = []

            with mock.patch.object(db, 'DB') as DB:
                db_mock = mock.MagicMock()
                db_mock.get_notebook_titles.return_value = ['Notebook']
                DB.return_value = db_mock

                backup_system.BackupSystem(self.view, self.DB_PATH).scan()

                sane_mock.open.assert_not_called()
                db_mock.save_notebook.assert_not_called()

    def test_scan_no_new_pages(self):
        scan_prefs = {
            'device': 'dev',
            'notebook': 'Notebook',
            'append': ''
        }

        self.view.ask_for_scan_prefs.return_value = scan_prefs

        with mock.patch('smth.backup_system.sane') as sane_mock:
            sane_mock.get_devices.return_value = []

            with mock.patch.object(db, 'DB') as DB:
                db_mock = mock.MagicMock()
                db_mock.get_notebook_titles.return_value = ['Notebook']
                DB.return_value = db_mock

                backup_system.BackupSystem(self.view, self.DB_PATH).scan()

                sane_mock.open.assert_not_called()
                db_mock.save_notebook.assert_not_called()

    def test_scan_db_error(self):
        with mock.patch('smth.backup_system.sane') as sane_mock:
            sane_mock.get_devices.return_value = []

            with mock.patch.object(db, 'DB') as DB:
                db_mock = mock.MagicMock()
                db_mock.get_notebook_titles.side_effect = db.Error
                DB.return_value = db_mock

                backup_system_= backup_system.BackupSystem(
                    self.view, self.DB_PATH)

                self.assertRaises(SystemExit, backup_system_.scan)

                self.view.ask_for_scan_prefs.assert_not_called()
                sane_mock.open.assert_not_called()
                db_mock.save_notebook.assert_not_called()

    def test_scan_keyboard_interrupt_during_scanning(self):
        scan_prefs = {
            'device': 'dev',
            'notebook': 'Notebook',
            'append': '3'
        }

        self.view.ask_for_scan_prefs.return_value = scan_prefs

        with mock.patch('smth.backup_system.sane') as sane_mock:
            scanner_mock = mock.MagicMock()
            scanner_mock.scan.side_effect = KeyboardInterrupt

            sane_mock.get_devices.return_value = []
            sane_mock.open.return_value = scanner_mock

            with mock.patch.object(db, 'DB') as DB:
                notebook_mock = mock.MagicMock()
                notebook_mock.title = 'Notebook'
                notebook_mock.path = '/test/path.pdf'
                notebook_mock.total_pages = 0

                db_mock = mock.MagicMock()
                db_mock.get_notebook_titles.return_value = ['Notebook']
                db_mock.get_notebook_by_title.return_value = notebook_mock
                DB.return_value = db_mock

                backup_system.BackupSystem(self.view, self.DB_PATH).scan()

                scanner_mock.close.assert_called_once()
                db_mock.save_notebook.assert_not_called()

    def test_scan_no_notebooks(self):
        with mock.patch.object(db, 'DB') as DB:
            db_mock = mock.MagicMock()
            db_mock.get_notebook_titles.return_value = []
            DB.return_value = db_mock

            with mock.patch('smth.backup_system.sane') as sane_mock:
                sane_mock = mock.MagicMock()

                backup_system.BackupSystem(self.view, self.DB_PATH).scan()

                sane_mock.init.assert_not_called()

    def tearDown(self):
        if os.path.exists(self.DB_PATH):
            os.remove(self.DB_PATH)

