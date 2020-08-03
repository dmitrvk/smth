# License: GNU GPL Version 3

"""The module provides ScanPreferences class for scanning setup.

    Typical usage example:

    pages_to_replace = [2, 5, 7]
    pages_to_append = [8, 9, 10]

    prefs = ScanPreferences()
    prefs.notebook = notebook
    prefs.pages_queue.extend(pages_to_replace)
    prefs.pages_queue.extend(pages_to_append)

    scanner_.scan(prefs)
"""

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
