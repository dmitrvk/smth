import collections
import itertools
import logging
import math
import time
from typing import List

import _sane
import PIL.Image as pillow
import sane

from smth import config, models

from . import callback, error, preferences

log = logging.getLogger(__name__)

Device = collections.namedtuple('Device', 'name vendor model type')


class Scanner:
    """Represents a scanner device which can scan notebooks."""

    def __init__(self, conf: config.Config):
        self.callback = None
        self.conf = conf

    @staticmethod
    def get_devices() -> List[Device]:
        """Load the list of available devices.

        Equivalent to call `scanimage -L`.
        Return the list with devices' names."""
        try:
            sane.init()
            return list(itertools.starmap(Device, sane.get_devices()))
        except _sane.error as exception:
            log.exception(exception)
            raise error.Error('Failed to load the list of devices')
        except KeyboardInterrupt as exception:
            log.exception(exception)
            raise error.Error(
                'Keyboard interrupt while loading the list of devices')
        finally:
            sane.exit()

    def register(self, callback_: callback.Callback) -> None:
        """Provide callback implementation to subscribe on scanner's events."""
        self.callback = callback_

    def scan(self, prefs: preferences.ScanPreferences) -> None:
        """Perform scanning with given preferences."""
        if not self.conf.scanner_device:
            if self.callback:
                self.callback.on_set_device()

        if not self.conf.scanner_device:
            self._handle_error('Device is not set.')
        else:
            device = None

            try:
                sane.init()
                device = self._get_device(self.conf.scanner_device)
                self._scan_with_prefs(device, prefs)

            except _sane.error as exception:
                log.exception(exception)
                self._handle_error(str(exception))

            except KeyboardInterrupt:
                log.error('Scan failed due to keyboard interrupt')
                self._handle_error('Keyboard interrupt')

            finally:
                if device:
                    device.close()

                sane.exit()

    def _get_device(self, device_name: str) -> sane.SaneDev:
        device = sane.open(device_name)
        device.format = 'jpeg'

        available_options = device.get_options()

        config_options = {}

        try:
            config_options = {
                'mode': self.conf.scanner_mode,
                'resolution': self.conf.scanner_resolution,
            }

            for conf_option in config_options:
                if hasattr(device, conf_option):
                    for option in available_options:
                        value = config_options[conf_option]
                        allowed_values = option[8]

                        if option[1] == conf_option:
                            if value in allowed_values:
                                setattr(device, conf_option, value)
                            else:
                                message = ("Wrong value "
                                           f"'{value}' for option "
                                           f"'{conf_option}' "
                                           "in config file.\n"
                                           f"Allowed values: {allowed_values}")
                                self._handle_error(message)
                else:
                    message = "Scanner '{conf_option}' option cannot be set."
                    self._handle_error(message)

        except config.Error as exception:
            self._handle_error(str(exception))

        return device

    def _scan_with_prefs(
            self,
            device: sane.SaneDev,
            prefs: preferences.ScanPreferences) -> None:
        """Perform actual scanning."""
        if len(prefs.pages_queue) == 0:
            self.callback.on_error('Nothing to scan')
            return

        if self.callback:
            self.callback.on_start(device.devname, list(prefs.pages_queue))

        while len(prefs.pages_queue) > 0:
            page = prefs.pages_queue.popleft()

            if self.callback:
                self.callback.on_start_scan_page(page)

            image = device.scan()

            if prefs.notebook.type.pages_paired:
                page_width_pt = math.ceil(
                    prefs.notebook.type.page_width * device.resolution / 25.4)
                orig_width = image.size[1]

                if (page_width_pt * 2 < orig_width and
                        prefs.notebook.first_page_number % 2 == page % 2):
                    # two pages on image, crop both left and right pages
                    self._process_scanned_page(
                        page, prefs.notebook, image, device.resolution)

                    self._process_scanned_page(
                        page + 1, prefs.notebook, image, device.resolution)

                    if prefs.pages_queue:
                        if prefs.pages_queue[0] == page + 1:
                            prefs.pages_queue.popleft()
                else:
                    self._process_scanned_page(
                        page, prefs.notebook, image, device.resolution)
            else:
                self._process_scanned_page(
                    page, prefs.notebook, image, device.resolution)

            if prefs.pages_queue:
                time.sleep(self.conf.scanner_delay)

        if self.callback:
            self.callback.on_finish(prefs.notebook)

    def _process_scanned_page(
            self, page: int, notebook: models.Notebook, image: pillow.Image,
            resolution: int) -> None:
        image = notebook.crop_image(
            page, image, resolution)

        if page > (notebook.total_pages +
                   notebook.first_page_number - 1):
            notebook.total_pages += 1

        if self.callback:
            self.callback.on_finish_scan_page(
                notebook, page, image)

    def _handle_error(self, message: str) -> None:
        """Call `on_error()` callback or raise an exception."""
        if self.callback:
            self.callback.on_error(message)
        else:
            raise error.Error(message)
