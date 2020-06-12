import logging
import unittest
from unittest import mock

import _sane
import sane

from smth import scanner


class ScannerTestCase(unittest.TestCase):
    """Test scanner operations."""

    def setUp(self):
        logging.disable()

        sane.init = mock.MagicMock()
        sane.get_devices = mock.MagicMock()
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
        conf = mock.MagicMock(**{
            'scanner_device': 'device',
        })

        sane.init.side_effect = _sane.error

        scanner_ = scanner.Scanner(conf)

        prefs = mock.MagicMock(**{
            'pages_queue': [1, 2, 3],
        })

        self.assertRaises(scanner.Error, scanner_.scan, prefs)
