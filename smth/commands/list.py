import logging
import sys
from typing import List

from smth import commands, db, view

log = logging.getLogger(__name__)


class ListCommand(commands.Command):  # pylint: disable=too-few-public-methods
    """Displays list of existing notebooks."""

    def __init__(self, db_: db.DB, view_: view.View):
        self.db = db_
        self.view = view_

    def execute(self, args: List[str] = None) -> None:
        """Get notebooks from database and show them to user."""
        try:
            notebooks = self.db.get_notebooks()
            self.view.show_notebooks(notebooks)
        except db.Error as exception:
            log.exception(exception)
            self.view.show_error(str(exception))
            sys.exit(1)
