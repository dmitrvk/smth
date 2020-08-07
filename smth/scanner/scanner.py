# License: GNU GPL Version 3

"""The module provides the Scanner class which is used to perform scanning.

    Typical usage example:

    scanner_ = scanner.Scanner(conf)
    scanner_.register(callback)

    try:
        scanner_.scan(prefs)
    except scanner.Error:
        pass
"""

import collections
import itertools
import logging
import math
import time

import _sane
import PIL.Image as pillow
import sane

from smth import config, models

from . import callback, preferences

log = logging.getLogger(__name__)

Device = collections.namedtuple('Device', 'name vendor model type')


class Scanner:
    """Represents a scanner device which can scan notebooks."""

    def __init__(self, conf: config.Config, callback_: callback.Callback):
        self._conf = conf
        self._callback = callback_

    def scan(self, prefs: preferences.ScanPreferences) -> None:
        """Performs scanning with the given preferences.

        Args:
            prefs:
                ScanPreferences objects with the information about the notebook
                and pages to scan.
        """
        if not self._conf.scanner_device:
            try:
                sane.init()

                self._callback.on_searching_for_devices()
                devices = list(itertools.starmap(Device, sane.get_devices()))

                if devices:
                    device_name = self._callback.on_set_device(devices)

                    if device_name:
                        self._conf.scanner_device = device_name
                    else:
                        self._callback.on_error('Device is not set.')
                else:
                    self._callback.on_error('No devices found.')

            except _sane.error as exception:
                log.exception(exception)
                self._callback.on_error('Failed to load the list of devices')

            except KeyboardInterrupt as exception:
                log.exception(exception)
                message = 'Keyboard interrupt while loading list of devices'
                self._callback.on_error(message)

            finally:
                sane.exit()

        device = None

        try:
            sane.init()

            device = self._get_device(self._conf.scanner_device)
            self._scan_with_prefs(device, prefs)

        except _sane.error as exception:
            log.exception(exception)
            self._callback.on_error(str(exception))

        except KeyboardInterrupt:
            log.error('Scan failed due to keyboard interrupt')
            self._callback.on_error('Keyboard interrupt')

        finally:
            if device:
                device.close()

            sane.exit()

    def _get_device(self, device_name: str) -> sane.SaneDev:
        """Opens the device and sets the parameters according to config.

        Args:
            device_name:
                Name of a scanner device.

        Returns:
            A sane.SaneDev object representing a SANE device.
        """
        device = sane.open(device_name)
        device.format = 'jpeg'

        available_options = device.get_options()

        config_options = {}

        try:  # pylint: disable=too-many-nested-blocks
            config_options = {
                'mode': self._conf.scanner_mode,
                'resolution': self._conf.scanner_resolution,
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
                                self._callback.on_error(message)
                else:
                    message = "Scanner '{conf_option}' option cannot be set."
                    self._callback.on_error(message)

        except config.Error as exception:
            self._callback.on_error(str(exception))

        return device

    def _scan_with_prefs(
            self,
            device: sane.SaneDev,
            prefs: preferences.ScanPreferences) -> None:
        """Performs the actual scanning.

        Args:
            device:
                A sane.SaneDev object representing a SANE device.
            prefs:
                A ScanPreferences object containing the information about the
                notebook and pages which should be scanned.
        """
        if len(prefs.pages_queue) == 0:
            self._callback.on_error('Nothing to scan')
            return

        self._callback.on_start(device.devname, list(prefs.pages_queue))

        while len(prefs.pages_queue) > 0:
            page = prefs.pages_queue.popleft()

            self._callback.on_start_scan_page(page)

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
                time.sleep(self._conf.scanner_delay)

        self._callback.on_finish(prefs.notebook)

    def _process_scanned_page(
            self, page: int, notebook: models.Notebook, image: pillow.Image,
            resolution: int) -> None:
        """Crops an image with page, increases total number of pages if needed.

        Args:
            page:
                Number of page which has been scanned.
            notebook:
                A notebook to which the page belongs.
            image:
                An image with the scanned page.  This image will be cropped and
                rotated as needed and saved to a file.
        """
        image = notebook.crop_image(
            page, image, resolution)

        if page > (notebook.total_pages +
                   notebook.first_page_number - 1):
            notebook.total_pages += 1

        self._callback.on_finish_scan_page(notebook, page, image)
