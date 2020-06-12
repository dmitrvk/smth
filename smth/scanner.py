import abc
import collections
import logging
import operator
import time
from typing import List

import _sane
import sane
import PIL.Image as pillow

from smth import config, models

log = logging.getLogger(__name__)


class Callback(abc.ABC):
    """Used to notify about scanner's events. Must be subclassed."""

    @abc.abstractmethod
    def on_set_device(self) -> None:
        """Called when no device is set.

        A proper device should be set in app config inside this method."""

    @abc.abstractmethod
    def on_start(self, device_name: str, pages_queue: List[int]) -> None:
        """Called when scanning process starts."""

    @abc.abstractmethod
    def on_start_scan_page(self, page: int) -> None:
        """Called when scanning of a page starts."""

    @abc.abstractmethod
    def on_finish_scan_page(
            self, notebook: models.Notebook, page: int,
            image: pillow.Image) -> None:
        """Called when scanning of a page finishes."""

    @abc.abstractmethod
    def on_finish(self, notebook: models.Notebook) -> None:
        """Called when scanning process finishes."""

    @abc.abstractmethod
    def on_error(self, message: str) -> None:
        """Called when error occurs when working with scanner."""


class ScanPreferences:
    """Used to specify what scanner should do."""

    def __init__(self):
        self._notebook = None
        self._append_queue = collections.deque()

    @property
    def notebook(self) -> models.Notebook:
        """A notebook which should be scanned."""
        return self._notebook

    @notebook.setter
    def notebook(self, notebook: models.Notebook) -> None:
        self._notebook = notebook

    @property
    def pages_queue(self) -> collections.deque:
        """Numbers of pages that should be scanned."""
        return self._append_queue


class Error(Exception):
    """An error which occurs when working with scanner."""


class Scanner:
    """Represents a scanner device which can scan notebooks."""

    DEVICE_PREFERENCES = {
        'format': 'jpeg',
        'mode': 'gray',
        'resolution': 150,
    }

    def __init__(self, conf: config.Config):
        self.callback = None
        self.conf = conf

    @staticmethod
    def get_devices() -> List[str]:
        """Load the list of available devices.

        Equivalent to call `scanimage -L`.
        Return the list with devices' names."""
        try:
            sane.init()
            devices = list(map(operator.itemgetter(0), sane.get_devices()))
            return devices
        except _sane.error as exception:
            log.exception(exception)
            raise Error('Failed to load the list of devices')
        except KeyboardInterrupt as exception:
            log.exception(exception)
            raise Error('Keyboard interrupt while loading the list of devices')
        finally:
            sane.exit()

    def register(self, callback: Callback) -> None:
        """Provide callback implementation to subscribe on scanner's events."""
        self.callback = callback

    def scan(self, prefs: ScanPreferences) -> None:
        """Perform scanning with given preferences."""
        if not self.conf.scanner_device:
            if self.callback:
                self.callback.on_set_device()

        if not self.conf.scanner_device:
            self._handle_error('Device is not set')
        else:
            device = None

            try:
                sane.init()
                device = self._get_device(self.conf.scanner_device)
                self._scan_with_prefs(device, prefs, self.callback)

            except _sane.error as exception:
                self._handle_error(str(exception))
                log.exception(exception)

            except KeyboardInterrupt:
                self._handle_error('Keyboard interrupt')
                log.error('Scan failed due to keyboard interrupt')

            finally:
                if device:
                    device.close()

                sane.exit()

    def _get_device(self, device_name: str) -> sane.SaneDev:
        device = sane.open(device_name)
        device.format = self.DEVICE_PREFERENCES['format']
        device.mode = self.DEVICE_PREFERENCES['mode']
        device.resolution = self.DEVICE_PREFERENCES['resolution']
        return device

    def _scan_with_prefs(
            self, device: sane.SaneDev, prefs: ScanPreferences,
            callback: Callback) -> None:
        """Perform actual scanning."""
        if len(prefs.pages_queue) == 0:
            callback.on_error('Nothing to scan')
            return

        if self.callback:
            self.callback.on_start(device.devname, list(prefs.pages_queue))

        while len(prefs.pages_queue) > 0:
            page = prefs.pages_queue.popleft()

            if callback:
                callback.on_start_scan_page(page)

            image = device.scan()

            if page >= prefs.notebook.total_pages:
                prefs.notebook.total_pages += 1

            if len(prefs.pages_queue) > 0:
                time.sleep(self.conf.scanner_delay)

            if callback:
                callback.on_finish_scan_page(
                    prefs.notebook, page, image)

        if self.callback:
            self.callback.on_finish(prefs.notebook)

    def _handle_error(self, message: str) -> None:
        """Call `on_error()` callback or raise an exception."""
        if self.callback:
            self.callback.on_error(message)
        else:
            raise Error(message)
