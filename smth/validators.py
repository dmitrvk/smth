import os

from .db import DB

class NotebookValidator:
    """Validate user input when manipulating notebooks."""
    def __init__(self, db: DB):
        self._db = db

    def validate(self, title: str, type: str, path: str, first: int):
        """Validate notebook's parameters.

        Raise ValueError if inacceptable.
        Raise DBError on database errors."""
        self.validate_title(title)
        self.validate_type(type)
        self.validate_path(path)
        self.validate_first_page_number(first)

    def validate_title(self, title: str) -> None:
        if len(title) == 0:
            raise ValueError('Title must not be empty')

        if self._db.notebook_exists(title):
            raise ValueError(f"Notebook '{title}' exists")

        pages_dir = os.path.expanduser(f'~/.local/share/smth/pages/{title}')
        if os.path.exists(pages_dir):
            raise FileExistsError(f"'{pages_dir}' already exists")

    def validate_type(self, type: str) -> None:
        if len(type.strip()) == 0:
            raise ValueError('Notebook type must not be empty')

        if not self._db.notebook_type_exists(type):
            raise ValueError(f"Type '{type}' does not exist")

    def validate_path(self, path: str) -> None:
        if len(path) == 0:
            raise ValueError('Path must not be empty')

        if os.path.exists(path):
            raise FileExistsError(f"'{path}' already exists")

    def validate_first_page_number(self, number: int) -> None:
        if not isinstance(number, int) or number < 0:
            raise ValueError("1st page number must be integer >= 0")
