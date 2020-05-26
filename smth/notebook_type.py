class NotebookType:
    """Contains information about notebook like its page size."""

    def __init__(self, title: str, page_width: int, page_height: int):
        self._id = -1
        self._title = title
        self._page_width = page_width
        self._page_height = page_height
        self._pages_paired = False

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        if title == None or len(title.strip()) == 0:
            self._title = 'Untitled'
        else:
            self._title = title.strip()

    @property
    def page_width(self):
        return self._page_width

    @page_width.setter
    def page_width(self, page_width):
        if page_width > 0:
            self._page_width = page_width
        else:
            self._page_width = 0

    @property
    def page_height(self):
        return self._page_height

    @page_height.setter
    def page_height(self, page_height):
        if page_height > 0:
            self._page_height = page_height
        else:
            self._page_height = 0

    def __repr__(self):
        repr = f"<NotebookType '{self._title}'"
        repr += f" of size '{self._page_width}x{self._page_height}mm'"
        if self._pages_paired:
            repr += f" with paired pages>"
        else:
            repr += '>'
        return repr

