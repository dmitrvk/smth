import os
import pathlib

from PyInquirer import ValidationError

from smth import db


class NotebookValidator:
    """Validate user input when manipulating notebooks."""
    def __init__(self, db: db.DB):
        self._db = db

    def validate_title(self, title: str) -> bool:
        title = title.strip()

        if len(title) == 0:
            raise ValidationError(message='Title must not be empty.')

        if self._db.notebook_exists(title):
            raise ValidationError(message=f"Notebook '{title}' exists")

        pages_dir = os.path.expanduser(f'~/.local/share/smth/pages/{title}')
        if os.path.exists(pages_dir):
            raise ValidationError(message=f"'{pages_dir}' already exists")

        return True

    def validate_type(self, type: str) -> bool:
        type = type.strip()

        if len(type.strip()) == 0:
            raise ValidationError(message='Notebook type must not be empty')

        if not self._db.type_exists(type):
            raise ValidationError(message=f"Type '{type}' does not exist")

        return True

    def validate_path(self, path: str) -> bool:
        path = path.strip()

        if len(path) == 0:
            raise ValidationError(message='Path must not be empty')

        path = pathlib.Path(os.path.expandvars(path)).expanduser().resolve()

        if not path.is_dir() and path.exists():
            raise ValidationError(message=f"'{path}' already exists")

        notebook = self._db.get_notebook_by_path(str(path))

        if notebook.title != 'Untitled':
            message = f"'{path}' already taken by notebook '{notebook.title}'"
            raise ValidationError(message=message)

        return True

    def validate_first_page_number(self, number: str) -> bool:
        number = number.strip()

        if not number.isnumeric():
            raise ValidationError(
                message='Please, enter a number from 0 to 100.')

        if len(number) > 3:
            raise ValidationError(
                message='Please, enter a number from 0 to 100')

        if int(number) > 100:
            raise ValidationError(
                message='Please, enter a number from 0 to 100')

        return True


class ScanPreferencesValidator:  # pylint: disable=too-few-public-methods
    """Validator for user input when choosing scan preferences."""

    def validate_number_of_pages_to_append(self, number: str) -> bool:  # pylint: disable=no-self-use  # noqa: E501
        """Allow empty value or an integer > 0."""
        if len(number.strip()) == 0:
            return True

        if not number.isnumeric():
            raise ValidationError(
                message='Please, enter a number from 0 to 100 or leave empty.')

        if len(number) > 3:
            raise ValidationError(
                message='Please, enter a number from 0 to 100 or leave empty.')

        if int(number) > 100:
            raise ValidationError(
                message='Please, enter a number from 0 to 100 or leave empty.')

        return True
