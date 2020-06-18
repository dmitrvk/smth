import logging
import unittest
from unittest import mock

import _sane
import sane

from smth import commands, db, scanner


class ScanCommandTestCase(unittest.TestCase):
    def setUp(self):
        logging.disable()

        self.notebook = mock.MagicMock(**{
            'title': 'Notebook',
            'path': '/test/path.pdf',
            'total_pages': 0,
        })

        self.db = mock.MagicMock(**{
            'get_notebook_titles.return_value': [self.notebook.title],
            'get_notebook_by_title.return_value': self.notebook,
        })

        self.scan_prefs = {
            'device': 'device',
            'notebook': self.notebook.title,
            'append': '3'
        }

        self.view = mock.MagicMock(**{
            'ask_for_scan_prefs.return_value': self.scan_prefs,
        })

        self.conf = mock.MagicMock(**{
            'scanner_device': None,
            'scanner_delay': 0,
        })

        self.pdf = mock.MagicMock()
        fpdf_patcher = mock.patch('fpdf.FPDF')
        fpdf_patcher.start().return_value = self.pdf
        self.addCleanup(fpdf_patcher.stop)

        self.image = mock.MagicMock(size=(100, 200))
        self.scanner = mock.MagicMock(**{'scan.return_value': self.image})

        sane.init = mock.MagicMock()
        sane.get_devices = mock.MagicMock(return_value=[])
        sane.open = mock.MagicMock(return_value=self.scanner)

    def test_execute_wrong_device_set(self):
        self.conf.scanner_device = 'dev'

        sane.open.side_effect = _sane.error

        command = commands.ScanCommand(self.db, self.view, self.conf)

        self.assertRaises(SystemExit, command.execute)
        self.db.save_notebook.assert_not_called()
        self.view.show_error.assert_called_once()

    def test_execute_keyboard_interrupt_when_searching_for_devices(self):
        sane.get_devices.side_effect = KeyboardInterrupt

        command = commands.ScanCommand(self.db, self.view, self.conf)

        self.assertRaises(SystemExit, command.execute)
        sane.open.assert_not_called()
        self.db.save_notebook.assert_not_called()

    def test_execute_cannot_open_device(self):
        sane.open.side_effect = _sane.error

        command = commands.ScanCommand(self.db, self.view, self.conf)

        self.assertRaises(SystemExit, command.execute)
        self.db.save_notebook.assert_not_called()
        self.view.show_error.assert_called()

    def test_execute_db_error(self):
        self.db.get_notebook_titles.side_effect = db.Error

        command = commands.ScanCommand(self.db, self.view, self.conf)

        self.assertRaises(SystemExit, command.execute)
        self.view.ask_for_scan_prefs.assert_not_called()
        sane.open.assert_not_called()
        self.db.save_notebook.assert_not_called()

    def test_execute_keyboard_interrupt_during_scanning(self):
        self.scanner.scan.side_effect = KeyboardInterrupt

        command = commands.ScanCommand(self.db, self.view, self.conf)

        self.assertRaises(SystemExit, command.execute)
        self.db.save_notebook.assert_not_called()

    def test_execute_sane_error(self):
        self.scanner.scan.side_effect = _sane.error

        command = commands.ScanCommand(self.db, self.view, self.conf)

        self.assertRaises(SystemExit, command.execute)
        self.db.save_notebook.assert_not_called()
        self.view.show_error.assert_called()

    def test_execute_scanner_error(self):
        with mock.patch('smth.scanner.Scanner') as Scanner:
            Scanner.return_value = mock.MagicMock(**{
                'scan.side_effect': scanner.Error,
            })

            command = commands.ScanCommand(self.db, self.view, self.conf)

            self.assertRaises(SystemExit, command.execute)
        self.db.save_notebook.assert_not_called()
        self.view.show_error.assert_called_once()

    def test_execute_no_notebooks(self):
        self.db.get_notebook_titles.return_value = []

        commands.ScanCommand(self.db, self.view, self.conf).execute()

        self.view.ask_for_scan_prefs.assert_not_called()
        self.scanner.scan.assert_not_called()

    def test_execute_with_set_device_option(self):
        args = ['--set-device']
        with mock.patch('smth.scanner.Scanner', return_value=mock.MagicMock()):
            commands.ScanCommand(self.db, self.view, self.conf).execute(args)
        self.assertEqual(self.conf.scanner_device, '')
