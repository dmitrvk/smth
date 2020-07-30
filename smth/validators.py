# License: GNU GPL Version 3

"""The module contains validators that are used to validate the user input.

Validators methonds should be used when constructing questions with
PyInquirer library.

    Typical usage example:

    database = db.DB('/path/to/smth.db')
    validator = NotebookValidator(database)

    questions = [
        {
            'type': 'input',
            'name': 'title',
            'message': 'Enter title:',
            'validate': validator.validate_title,
        },
    ]

    answers = inquirer.prompt(questions)
"""

import operator
import os
import pathlib
from typing import NoReturn

from PyInquirer import ValidationError

from smth import db, models


class NotebookValidator:
    """Validate user input when manipulating notebooks."""
    def __init__(self, db_: db.DB):
        self._db = db_

    def validate_title(self, title: str) -> bool:
        """Check if title is not empty and not already taken."""
        title = title.strip()

        if len(title) == 0:
            raise ValidationError(message='Title must not be empty.')

        if self._db.notebook_exists(title):
            raise ValidationError(message=f"Notebook '{title}' exists")

        pages_dir = os.path.expanduser(f'~/.local/share/smth/pages/{title}')
        if os.path.exists(pages_dir):
            raise ValidationError(message=f"'{pages_dir}' already exists")

        return True

    def validate_type(self, type_: str) -> bool:
        """Check if type is not empty and exists."""
        type_ = type_.strip()

        if len(type_.strip()) == 0:
            raise ValidationError(message='Notebook type must not be empty')

        if not self._db.type_exists(type_):
            raise ValidationError(message=f"Type '{type_}' does not exist")

        return True

    def validate_path(self, path: str) -> bool:
        """Check if path is not empty and not already taken."""
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

    def validate_first_page_number(self, number: str) -> bool:  # pylint: disable=no-self-use  # noqa: E501
        """Check if number is an integer from 0 to 100."""
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


class NotebookUpdateValidator:
    """Validate user input when updating a notebook."""
    def validate_title(self, title: str) -> bool:  # pylint: disable=no-self-use  # noqa: E501
        """Check if title is not empty."""
        title = title.strip()

        if len(title) == 0:
            raise ValidationError(message='Title must not be empty.')

        return True

    def validate_path(self, path: str) -> bool:  # pylint: disable=no-self-use  # noqa: E501
        """Check if path is not empty."""
        path = path.strip()

        if len(path) == 0:
            raise ValidationError(message='Path must not be empty')

        return True


class TypeValidator:
    """Validate user input when manipulating types."""
    def __init__(self, db_: db.DB):
        self._db = db_

    def validate_title(self, title: str) -> bool:
        """Check if title is not empty and not already taken."""
        title = title.strip()

        if len(title) == 0:
            raise ValidationError(message='Title must not be empty.')

        if self._db.type_exists(title):
            raise ValidationError(message=f"Type '{title}' exists")

        return True

    def validate_page_size(self, size: str) -> bool:  # pylint: disable=no-self-use  # noqa: E501
        """Check if given input is an integer from 10 to 1000."""
        size = size.strip()

        if not size.isnumeric():
            raise ValidationError(
                message='Please, enter a number from 10 to 1000')

        if int(size) < 10 or int(size) > 1000:
            raise ValidationError(
                message='Please, enter a number from 10 to 1000')

        return True


class ScanPreferencesValidator:  # pylint: disable=too-few-public-methods
    """Validator for user input when choosing scan preferences."""

    def __init__(self, notebook: models.Notebook):
        self._notebook = notebook

    def validate_number_of_pages_to_append(self, number: str) -> bool:  # pylint: disable=no-self-use  # noqa: E501
        """Check if number is an integer from 0 to 100.

        Allow empty value."""
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

    def validate_pages_to_replace(self, pages: str) -> bool:
        """Check if given string with pages is correct.

        Given string must contain integers with page numbers separated with a
        space.  Ranges (e.g. 3-5) are allowed.  Pages must exist in a
        notebook."""
        def raise_error(item: str, reason: str) -> NoReturn:
            raise ValidationError(
                message=f"'{item}' is invalid: {reason}.")

        replace = pages.strip().split()
        replace = list(map(operator.methodcaller('strip'), replace))
        replace = list(filter(lambda s: s != '', replace))

        min_page = self._notebook.first_page_number
        max_page = min_page + self._notebook.total_pages - 1

        for item in replace:
            if item.isnumeric():
                page = int(item)

                if not min_page <= page <= max_page:
                    raise_error(
                        item, f'page must be from {min_page} to {max_page}')
            else:
                if item.count('-') == 1:
                    range_start, range_end = item.split('-')

                    if range_start.isnumeric() and range_end.isnumeric():
                        range_start = int(range_start)
                        range_end = int(range_end)

                        if range_start > range_end:
                            raise_error(item, 'range start > end')
                        elif not min_page <= range_start <= max_page:
                            raise_error(
                                item,
                                f'page must be from {min_page} to {max_page}')
                        elif not min_page <= range_end <= max_page:
                            raise_error(
                                item,
                                f'page must be from {min_page} to {max_page}')
                    else:
                        raise_error(item, 'not a valid number')
                else:
                    raise_error(item, 'range is not valid')

        return True
