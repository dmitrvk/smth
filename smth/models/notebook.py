import pathlib

from .notebook_type import NotebookType


class Notebook:  # pylint: disable=too-many-instance-attributes
    """Collection of pages orderded by their numbers."""

    PAGES_ROOT = pathlib.Path('~/.local/share/smth/pages').expanduser()

    def __init__(self, title: str, notebook_type: NotebookType, path: str):
        self._id = -1
        self.title = title
        self._type = notebook_type
        self._path = path
        self._first_page_number = 1
        self._total_pages = 0

    @property
    def id(self) -> int:  # pylint: disable=invalid-name
        """Notebook's id in the database."""
        return self._id

    @id.setter
    def id(self, id_) -> None:  # pylint: disable=invalid-name
        self._id = id_

    @property
    def title(self) -> str:
        """Title of the notebook. Must be unique."""
        return self._title

    @title.setter
    def title(self, title: str) -> None:
        self._title = title if title else 'Untitled'

    @property
    def type(self) -> NotebookType:
        """Type of the notebook (page size, etc.)."""
        return self._type

    @property
    def path(self) -> int:
        """Path to PDF file in the filesystem."""
        return self._path

    @path.setter
    def path(self, path) -> None:
        self._path = path

    @property
    def total_pages(self) -> int:
        """Number of pages in the notebook."""
        return self._total_pages

    @total_pages.setter
    def total_pages(self, total_pages) -> None:
        if total_pages >= 0:
            self._total_pages = total_pages
        else:
            total_pages = 0

    @property
    def first_page_number(self) -> int:
        """A number from which page numbering should start."""
        return self._first_page_number

    @first_page_number.setter
    def first_page_number(self, number) -> None:
        if number >= 0:
            self._first_page_number = number
        else:
            self._first_page_number = 1

    def get_page_path(self, page: int) -> pathlib.Path:
        """Return absolute path to notebook's page with given number."""
        return self.PAGES_ROOT / self.title / f'{page}.jpg'

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                other.title == self.title)

    def __repr__(self):
        return f"<Notebook '{self._title}' of type '{self._type.title}'>"
