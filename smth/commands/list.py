# License: GNU GPL Version 3

"""The module provides `list` command for displaying available notebooks."""

import logging
from typing import List

from smth import db

from . import command

log = logging.getLogger(__name__)


class ListCommand(command.Command):  # pylint: disable=too-few-public-methods
    """Displays list of existing notebooks."""

    def execute(self, args: List[str] = None) -> None:
        """Gets the notebooks from database and shows them to user."""
        try:
            notebooks = self._db.get_notebooks()
            self._view.show_notebooks(notebooks)
        except db.Error as exception:
            self.exit_with_error(exception)
