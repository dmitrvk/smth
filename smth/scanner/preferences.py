import collections

from smth import models


class ScanPreferences:
    """Used to specify what scanner should do."""

    def __init__(self):
        self._notebook = None
        self._pages_queue = collections.deque()

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
        return self._pages_queue

    def __eq__(self, other):
        return (self.notebook.title == other.notebook.title and
                self.pages_queue == other.pages_queue)
