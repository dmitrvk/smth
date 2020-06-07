import logging
import sys

from smth import db, views

log = logging.getLogger(__name__)


class TypesController:
    """Displays list of existing notebooks."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def show_types_list(self) -> None:
        """Get notebook types from database and show them to user."""
        view = views.TypesView()

        try:
            db_ = db.DB(self.db_path)
            types = db_.get_types()
            view.show_types(types)

        except db.Error as exception:
            log.exception(exception)
            view.show_error(str(exception))
            sys.exit(1)
