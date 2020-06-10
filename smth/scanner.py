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
    @abc.abstractmethod
    def on_set_device(self) -> None: pass

    @abc.abstractmethod
    def on_start(self, device_name: str, pages_queue: List[int]) -> None: pass

    @abc.abstractmethod
    def on_start_scan_page(self, page: int) -> None: pass

    @abc.abstractmethod
    def on_finish_scan_page(
        self, notebook: models.Notebook, page: int,
        image: pillow.Image) -> None: pass

    @abc.abstractmethod
    def on_finish(self, notebook: models.Notebook) -> None: pass

    @abc.abstractmethod
    def on_error(self, message: str) -> None: pass


class ScanPreferences:
    def __init__(self):
        self._notebook = None
        self._append_queue = collections.deque()

    @property
    def notebook(self) -> models.Notebook:
        return self._notebook

    @notebook.setter
    def notebook(self, notebook: models.Notebook) -> None:
        self._notebook = notebook

    @property
    def pages_queue(self) -> collections.deque:
        return self._append_queue


class Error(Exception):
    pass


class Scanner:
    def __init__(self, conf: config.Config):
        self.callback = None
        self.conf = conf

    @staticmethod
    def get_devices() -> List[str]:
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
            return
        finally:
            sane.exit()

    def register(self, callback: Callback) -> None:
        self.callback = callback

    def scan(self, prefs: ScanPreferences) -> None:
        if not self.conf.scanner_device:
            if self.callback:
                self.callback.on_set_device()

        if not self.conf.scanner_device:
            if self.callback:
                self.callback.on_error('Device is not set')
                return
            else:
                raise Error('Device is not set')

        device = None

        try:
            sane.init()
            device = self._get_device(self.conf.scanner_device)
            self._scan_with_prefs(device, prefs, self.callback)

        except _sane.error as exception:
            log.exception(exception)

            if self.callback:
                self.callback.on_error(exception)
            else:
                raise Error(f'Scan failed: {exception}')

        except KeyboardInterrupt:
            log.error('Scan failed due to keyboard interrupt')

            if self.callback:
                self.callback.on_error('Keyboard interrupt')
            else:
                raise Error('Scan failed due to keyboard interrupt')

        finally:
            if device:
                device.close()

            sane.exit()

    def _get_device(self, device_name: str) -> sane.SaneDev:
        device = sane.open(device_name)
        device.format = 'jpeg'
        device.mode = 'gray'
        device.resolution = 150
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
