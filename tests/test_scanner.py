import collections
import logging
import math
import unittest
from unittest import mock

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
            'scanner_mode': 'Gray',
            'scanner_resolution': 150,
        })

        sane.init = mock.MagicMock()
        sane.scan = mock.MagicMock()
        sane.get_devices = mock.MagicMock()

        self.image = Image.new('RGB', (1280, 1760))

        self.device = mock.MagicMock(**{
            'devname': 'device',
            'scan.return_value': self.image,
            'mode': 'Gray',
            'resolution': self.conf.scanner_resolution,
            'get_options.return_value': [
                (1, 'mode', None, None, None, None, None, None,
                 ['Gray', 'Color']),
                (2, 'resolution', None, None, None, None, None, None,
                 [75, 150, 300, 600]),
            ],
        })

        self.callback = mock.MagicMock()

        sane.open = mock.MagicMock(return_value=self.device)
        sane.exit = mock.MagicMock()

    def test_scan_keyboard_interrupt(self):
        sane.open.side_effect = KeyboardInterrupt

        scanner_ = scanner.Scanner(self.conf, self.callback)

        notebook = models.Notebook('', models.NotebookType('', 0, 0), '')
        pages_queue = collections.deque()
        scanner_.scan(notebook, pages_queue)

        sane.scan.assert_not_called()
        self.callback.on_error.assert_called_once()
        sane.exit.assert_called_once()

    def test_scan(self):
        type_ = models.NotebookType('', 210, 297)
        notebook = models.Notebook('', type_, '')

        pages_queue = collections.deque()
        pages_queue.extend([1, 2, 3])

        scanner_ = scanner.Scanner(self.conf, self.callback)
        scanner_.scan(notebook, pages_queue)

        self.callback.on_start.assert_called_once_with('device', [1, 2, 3])
        self.callback.on_start_scan_page.assert_has_calls([
            mock.call(1),
            mock.call(2),
            mock.call(3),
        ])

        page_width_pt = math.ceil(type_.page_width * 150 / 25.4)
        page_height_pt = math.ceil(type_.page_height * 150 / 25.4)

        self.image = self.image.crop((0, 0, page_width_pt, page_height_pt))

        self.callback.on_finish_scan_page.assert_has_calls([
            mock.call(notebook, 1, self.image),
            mock.call(notebook, 2, self.image),
            mock.call(notebook, 3, self.image),
        ])

        self.assertEqual(notebook.total_pages, 3)

    def test_scan_paired_pages(self):
        type_ = models.NotebookType('', 160, 200)
        type_.pages_paired = True
        notebook = models.Notebook('', type_, '')

        pages_queue = collections.deque()
        pages_queue.extend([1, 2, 3])

        scanner_ = scanner.Scanner(self.conf, self.callback)
        scanner_.scan(notebook, pages_queue)

        self.callback.on_start.assert_called_once_with('device', [1, 2, 3])
        self.callback.on_start_scan_page.assert_has_calls([
            mock.call(1),
            mock.call(2),
            mock.call(3),
        ])

        page_width_pt = math.ceil(type_.page_width * 150 / 25.4)
        page_height_pt = math.ceil(type_.page_height * 150 / 25.4)

        self.image = self.image.crop((0, 0, page_width_pt, page_height_pt))

        self.callback.on_finish_scan_page.assert_has_calls([
            mock.call(notebook, 1, self.image),
            mock.call(notebook, 2, self.image),
            mock.call(notebook, 3, self.image),
        ])

        self.assertEqual(notebook.total_pages, 3)

    def test_scan_two_pages_at_once(self):
        type_ = models.NotebookType('', 100, 200)
        type_.pages_paired = True
        notebook = models.Notebook('', type_, '')

        pages_queue = collections.deque()
        pages_queue.extend([1, 2, 3])

        scanner_ = scanner.Scanner(self.conf, self.callback)
        scanner_.scan(notebook, pages_queue)

        self.callback.on_start.assert_called_once_with('device', [1, 2, 3])

        self.callback.on_start_scan_page.assert_has_calls([
            mock.call(1),
            mock.call(3),
        ])

        page_width_pt = math.ceil(type_.page_width * 150 / 25.4)
        page_height_pt = math.ceil(type_.page_height * 150 / 25.4)

        self.image = self.image.crop((0, 0, page_width_pt, page_height_pt))

        self.callback.on_finish_scan_page.assert_has_calls([
            mock.call(notebook, 1, self.image),
            mock.call(notebook, 2, self.image),
            mock.call(notebook, 3, self.image),
            mock.call(notebook, 4, self.image),
        ])

        self.assertEqual(notebook.total_pages, 4)

    def test_scan_nothing_to_scan(self):
        scanner_ = scanner.Scanner(self.conf, self.callback)
        notebook = models.Notebook('', models.NotebookType('', 0, 0), '')
        pages_queue = collections.deque()
        scanner_.scan(notebook, pages_queue)

        sane.scan.assert_not_called()
        self.callback.on_error.assert_called_once()
