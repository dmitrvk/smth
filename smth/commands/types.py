import logging
import sys
from typing import List

from smth import db, view

from . import command

log = logging.getLogger(__name__)


class TypesCommand(command.Command):  # pylint: disable=too-few-public-methods
    """Displays list of existing notebooks."""

    def __init__(self, db_: db.DB, view_: view.View):
        self._db = db_
        self.view = view_

    def execute(self, args: List[str] = None) -> None:
        """Get notebook types from database and show them to user."""
        try:
            types = self._db.get_types()
            self.view.show_types(types)
        except db.Error as exception:
            log.exception(exception)
            self.view.show_error(str(exception))
            sys.exit(1)
