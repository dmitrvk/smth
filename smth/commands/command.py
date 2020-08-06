# License: GNU GPL Version 3

"""The module provides the abstract Command class."""

import abc
import logging
import sys
from typing import List, NoReturn, Union

from smth import db, view

log = logging.getLogger(__name__)


class Command(abc.ABC):  # pylint: disable=too-few-public-methods
    """A command which can be executed with arguments."""

    def __init__(self, db_: db.DB, view_: view.View):
        self._db = db_
        self._view = view_

    @abc.abstractmethod
    def execute(self, args: List[str] = None):
        """Runs command with the given arguments.

        Args:
            args:
                A list of arguments passed to the command.
        """

    def exit_with_error(self, error: Union[Exception, str]) -> NoReturn:
        """Show error to user, log error message and exit with code 1.

        Args:
            error:
                An error that occured.  It can be an Exception object or a
                string with an error message.
        """
        if isinstance(error, Exception):
            self._view.show_error(str(error))
            log.exception(error)
        elif isinstance(error, str):
            self._view.show_error(error)
            log.error(error)

        sys.exit(1)

    def get_notebook_titles_from_db(self) -> List[str]:
        """Return the list of titles of all notebooks in the database.

        Returns:
            A list of notebooks' titles.
        """
        try:
            return self._db.get_notebook_titles()
        except db.Error as exception:
            self.exit_with_error(exception)
