import logging
import sys

from smth import db, view

log = logging.getLogger(__name__)


class ListController:
    """Displays list of existing notebooks."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.view = view.View()

    def show_notebooks_list(self) -> None:
        """Get notebooks from database and show them to user."""

        try:
            db_ = db.DB(self.db_path)
            notebooks = db_.get_notebooks()
            self.view.show_notebooks(notebooks)

        except db.Error as exception:
            log.exception(exception)
            self.view.show_error(str(exception))
            sys.exit(1)
