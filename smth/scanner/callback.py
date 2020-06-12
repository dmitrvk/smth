import abc
from typing import List

import PIL.Image as pillow

from smth import models


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
