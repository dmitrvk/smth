import abc
import logging
import sys
from typing import List, NoReturn

from smth import db, view

log = logging.getLogger(__name__)


class Command(abc.ABC):  # pylint: disable=too-few-public-methods
    """A command which can be executed with arguments."""

    def __init__(self, db_: db.DB, view_: view.View):
        self._db = db_
        self.view = view_

    @abc.abstractmethod
    def execute(self, args: List[str] = None):
        """Run command with the given arguments."""

    def exit_with_error(self, error: [Exception, str]) -> NoReturn:
        """Show error to user, log error message and exit with code 1."""
        if isinstance(error, Exception):
            self.view.show_error(str(error))
            log.exception(error)
        elif isinstance(error, str):
            self.view.show_error(error)
            log.error(error)

        sys.exit(1)
