# License: GNU GPL Version 3

"""The module provides scanner callback to subscribe on scanner's events.

    Typical usage example:

    class ScannerCallback(scanner.Callback):
        def __init__(self, ...):
            ...
        def on_searching_for_devices(self):
            ...
        # Overrride all methods

    scanner_ = scanner.Scanner(conf)
    scanner_.register(ScannerCallback(...))
"""

import abc
from typing import List

import PIL.Image as pillow

from smth import models


class Callback(abc.ABC):
    """Used to notify about scanner's events. Must be subclassed."""

    @abc.abstractmethod
    def on_searching_for_devices(self):
        """Called just before the searching starts."""

    @abc.abstractmethod
    def on_set_device(self) -> None:
        """Called when no device is set.

        A proper device should be set in the app config inside this method.
        """

    @abc.abstractmethod
    def on_start(self, device_name: str, pages_queue: List[int]) -> None:
        """Called when scanning process starts.

        Args:
            device_name:
                Name of the device which is used to perform scanning process.
            pages_queue:
                A list of pages the scanner is going to scan.
        """

    @abc.abstractmethod
    def on_start_scan_page(self, page: int) -> None:
        """Called when scanning of a page starts.

        Args:
            page:
                A number of page the scanner is going to scan.
        """

    @abc.abstractmethod
    def on_finish_scan_page(
            self, notebook: models.Notebook, page: int,
            image: pillow.Image) -> None:
        """Called when scanning of a page finishes.

        Args:
            notebook:
                A notebook which is being scanned.
            page:
                A number of page which the scanner just scanned.
            image:
                An image with the scanned page.
        """

    @abc.abstractmethod
    def on_finish(self, notebook: models.Notebook) -> None:
        """Called when the scanning process finishes.

        Args:
            notebook:
                A notebook which was scanned.
        """

    @abc.abstractmethod
    def on_error(self, message: str) -> None:
        """Called when error occurs when working with scanner.

        Args:
            message:
                An error message.
        """
