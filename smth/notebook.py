import os

from .notebook_type import NotebookType


class Notebook:
    """Notebook is a collection of pages orderded by their numbers."""

    def __init__(self, title: str, notebook_type: NotebookType, path: str):
        self._title = title
        self._type = notebook_type
        self._path = path
        self._first_page_number = 1
        self._total_pages = 0

    def __repr__(self):
        return f"<Notebook '{self._title}' of type '{self._type.title}'>"

