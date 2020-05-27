import os

from .notebook_type import NotebookType


class Notebook:
    """Collection of pages orderded by their numbers."""

    def __init__(self, title: str, notebook_type: NotebookType, path: str):
        self._id = -1
        self.title = title
        self._type = notebook_type
        self._path = path
        self._first_page_number = 1
        self._total_pages = 0

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, id) -> None:
        self._id = id

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, title: str) -> None:
        self._title = title if title else 'Untitled'

    @property
    def type(self) -> NotebookType:
        return self._type

    @property
    def path(self) -> int:
        return self._path

    @path.setter
    def path(self, path) -> None:
        self._path = path

    @property
    def total_pages(self) -> int:
        return self._total_pages

    @total_pages.setter
    def total_pages(self, total_pages) -> None:
        if total_pages >= 0:
            self._total_pages = total_pages
        else:
            total_pages = 0

    @property
    def first_page_number(self) -> int:
        return self._first_page_number

    @first_page_number.setter
    def first_page_number(self, number) -> None:
        if number >= 0:
            self._first_page_number = number
        else:
            self._first_page_number = 1

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                other.title == self.title)

    def __repr__(self):
        return f"<Notebook '{self._title}' of type '{self._type.title}'>"

