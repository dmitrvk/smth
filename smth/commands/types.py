import logging
from typing import List

from smth import db

from . import command

log = logging.getLogger(__name__)


class TypesCommand(command.Command):  # pylint: disable=too-few-public-methods
    """Displays list of existing notebooks."""

    def execute(self, args: List[str] = None) -> None:
        """Get notebook types from database and show them to user."""
        try:
            types = self._db.get_types()
            self.view.show_types(types)
        except db.Error as exception:
            self._exit_with_error(exception)
