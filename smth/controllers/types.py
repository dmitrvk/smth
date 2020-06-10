import logging
import sys

from smth import db, view

log = logging.getLogger(__name__)


class TypesController:
    """Displays list of existing notebooks."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.view = view.View()

    def show_types_list(self) -> None:
        """Get notebook types from database and show them to user."""

        try:
            db_ = db.DB(self.db_path)
            types = db_.get_types()
            self.view.show_types(types)

        except db.Error as exception:
            log.exception(exception)
            self.view.show_error(str(exception))
            sys.exit(1)
