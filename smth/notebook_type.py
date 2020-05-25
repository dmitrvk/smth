class NotebookType:
    """Contains information about notebook like its page size."""

    def __init__(self, title: str, page_width: int, page_height: int):
        self._title = title
        self._page_width = page_width
        self._page_height = page_height
        self._pages_paired = False

    @property
    def title(self):
        return self._title

    @property
    def page_width(self):
        return self._page_width

    @property
    def page_height(self):
        return self._page_height

    def __repr__(self):
        repr = f"<NotebookType '{self._title}'"
        repr += f" of size '{self._page_width}x{self._page_height}mm'"
        if self._pages_paired:
            repr += f" with paired pages>"
        else:
            repr += '>'
        return repr

