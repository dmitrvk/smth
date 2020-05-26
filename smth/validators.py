import os

from inquirer.errors import ValidationError

from smth.db import DB


class NotebookValidator:
    """Validate user input when manipulating notebooks."""
    def __init__(self, db: DB):
        self._db = db

    def validate_title(self, answers: dict, title: str) -> bool:
        title = title.strip()

        if len(title) == 0:
            raise ValidationError('', reason='Title must not be empty.')

        if self._db.notebook_exists(title):
            raise ValidationError('', reason=f"Notebook '{title}' exists")

        pages_dir = os.path.expanduser(f'~/.local/share/smth/pages/{title}')
        if os.path.exists(pages_dir):
            raise ValidationError('', reason=f"'{pages_dir}' already exists")

        return True

    def validate_type(self, answers: dict, type: str) -> bool:
        type = type.strip()

        if len(type.strip()) == 0:
            raise ValidationError('', reason='Notebook type must not be empty')

        if not self._db.notebook_type_exists(type):
            raise ValidationError('', reason=f"Type '{type}' does not exist")

        return True

    def validate_path(self, answers: dict, path: str) -> bool:
        path = path.strip()

        if len(path) == 0:
            raise ValidationError('', reason='Path must not be empty')

        if os.path.exists(path):
            raise ValidationError('', reason=f"'{path}' already exists")

        return True

    def validate_first_page_number(self, answers: dict, number: str) -> bool:
        number = number.strip()

        if not number.isnumeric():
            raise ValidationError('', reason='Please, enter an integer >= 0.')

        return True


class ScanPreferencesValidator:
    """Validator for user input when choosing scan preferences."""

    def validate_number_of_pages_to_append(
            self, answers: dict, number: str) -> bool:
        """Allow empty value or an integer > 0."""
        if len(number.strip()) == 0:
            return True

        if not number.isnumeric():
            raise ValidationError(
                '', reason='Please, enter an integer > 0 or leave empty.')

        if int(number) <= 0:
            raise ValidationError(
                '', reason='Please, enter an integer > 0 or leave empty.')

        return True

