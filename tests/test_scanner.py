import logging
import math
import unittest
from unittest import mock

import _sane
import sane
from PIL import Image

from smth import models, scanner


class ScannerTestCase(unittest.TestCase):
    """Test scanner operations."""

    def setUp(self):
        logging.disable()

        self.conf = mock.MagicMock(**{
            'scanner_device': 'device',
            'scanner_delay': 0,
        })

        sane.init = mock.MagicMock()
        sane.scan = mock.MagicMock()
        sane.get_devices = mock.MagicMock()

        self.image = Image.new('RGB', (1000, 2000))

        self.device = mock.MagicMock(**{
            'devname': 'device',
            'scan.return_value': self.image,
        })

        sane.open = mock.MagicMock(return_value=self.device)
        sane.exit = mock.MagicMock()

    def test_get_devices(self):
        sane_devices = [('device', 'vendor', 'model', 'type')]
        sane.get_devices.return_value = sane_devices

        devices = scanner.Scanner.get_devices()
        expected = [scanner.Device(*sane_devices[0])]

        self.assertListEqual(devices, expected)

    def test_get_devices_sane_error(self):
        sane.get_devices.side_effect = _sane.error
        self.assertRaises(scanner.Error, scanner.Scanner.get_devices)
        sane.exit.assert_called_once()

    def test_get_devices_keyboard_interrupt(self):
        sane.get_devices.side_effect = KeyboardInterrupt
        self.assertRaises(scanner.Error, scanner.Scanner.get_devices)
        sane.exit.assert_called_once()

    def test_scan_error_without_callback(self):
        """If no callback provided, scanner should raise `scanner.Error`."""
        sane.init.side_effect = _sane.error

        scanner_ = scanner.Scanner(self.conf)

        prefs = scanner.ScanPreferences()
        prefs.pages_queue.extend([1, 2, 3])

        self.assertRaises(scanner.Error, scanner_.scan, prefs)

    def test_scan_two_pages_at_once(self):
        type_ = models.NotebookType('', 100, 200)
        type_.pages_paired = True
        notebook = models.Notebook('', type_, '')

        prefs = scanner.ScanPreferences()
        prefs.notebook = notebook
        prefs.pages_queue.extend([1, 2, 3])

        callback = mock.MagicMock()

        scanner_ = scanner.Scanner(self.conf)
        scanner_.register(callback)

        scanner_.scan(prefs)

        callback.on_start.assert_called_once_with('device', [1, 2, 3])

        callback.on_start_scan_page.assert_has_calls([
            mock.call(1),
            mock.call(3),
        ])

        page_width_pt = math.ceil(type_.page_width * 150 / 25.4)
        page_height_pt = math.ceil(type_.page_height * 150 / 25.4)

        self.image = self.image.crop((0, 0, page_width_pt, page_height_pt))

        callback.on_finish_scan_page.assert_has_calls([
            mock.call(notebook, 1, self.image),
            mock.call(notebook, 2, self.image),
            mock.call(notebook, 3, self.image),
            mock.call(notebook, 4, self.image),
        ])

        self.assertEqual(notebook.total_pages, 4)
