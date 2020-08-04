# License: GNU GPL Version 3

"""The module provides the Notebook Type model."""


class NotebookType:  # pylint: disable=too-many-instance-attributes
    """Contains information about notebook like its page size."""

    def __init__(self, title: str, page_width: int, page_height: int):
        self._id = -1
        self.title = title
        self.page_width = page_width
        self.page_height = page_height
        self.pages_paired = False

    @property
    def id(self):  # pylint: disable=invalid-name
        """Object's id in the database."""
        return self._id

    @id.setter
    def id(self, id_):  # pylint: disable=invalid-name
        self._id = id_

    @property
    def title(self):
        """Type's title, e.g. 'A4'."""
        return self._title

    @title.setter
    def title(self, title):
        if title is None or len(title.strip()) == 0:
            self._title = 'Untitled'
        else:
            self._title = title.strip()

    @property
    def page_width(self):
        """Width of a page of a notebook with this type."""
        return self._page_width

    @page_width.setter
    def page_width(self, page_width):
        if page_width > 0:
            self._page_width = page_width
        else:
            self._page_width = 0

    @property
    def page_height(self):
        """Height of a page of a notebook with this type."""
        return self._page_height

    @page_height.setter
    def page_height(self, page_height):
        if page_height > 0:
            self._page_height = page_height
        else:
            self._page_height = 0

    @property
    def pages_paired(self) -> bool:
        """Indicates whether pages in a notebook should be paired in PDF."""
        return self._pages_paired

    @pages_paired.setter
    def pages_paired(self, paired):
        if isinstance(paired, bool):
            self._pages_paired = paired
        else:
            self._pages_paired = False

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                other.title == self.title)

    def __repr__(self):
        repr_ = f"<NotebookType '{self._title}'"
        repr_ += f" of size {self._page_width}x{self._page_height}mm"
        if self._pages_paired:
            repr_ += " with paired pages>"
        else:
            repr_ += '>'
        return repr_
