import collections
import itertools
import logging
import time
from typing import List

import _sane
import sane

from smth import config, scanner

log = logging.getLogger(__name__)

Device = collections.namedtuple('Device', 'name vendor model type')


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
    def get_devices() -> List[Device]:
        """Load the list of available devices.

        Equivalent to call `scanimage -L`.
        Return the list with devices' names."""
        try:
            sane.init()
            return list(itertools.starmap(Device, sane.get_devices()))
        except _sane.error as exception:
            log.exception(exception)
            raise scanner.Error('Failed to load the list of devices')
        except KeyboardInterrupt as exception:
            log.exception(exception)
            raise scanner.Error(
                'Keyboard interrupt while loading the list of devices')
        finally:
            sane.exit()

    def register(self, callback: scanner.Callback) -> None:
        """Provide callback implementation to subscribe on scanner's events."""
        self.callback = callback

    def scan(self, prefs: scanner.ScanPreferences) -> None:
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
            self, device: sane.SaneDev, prefs: scanner.ScanPreferences,
            callback: scanner.Callback) -> None:
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
            raise scanner.Error(message)
