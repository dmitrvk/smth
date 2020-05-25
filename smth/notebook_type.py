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

