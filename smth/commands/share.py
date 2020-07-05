import logging
from typing import List

from smth import db, cloud, view

from . import command

log = logging.getLogger(__name__)


class ShareCommand(command.Command):  # pylint: disable=too-few-public-methods
    """A command for sharing notebooks."""

    def __init__(self, db_: db.DB, view_: view.View, cloud_: cloud.Cloud):
        super().__init__(db_, view_)
        self._cloud = cloud_

    def execute(self, args: List[str] = None):
        """Share notebook and show a link."""
        try:
            notebooks = self._db.get_notebook_titles()
        except db.Error as exception:
            self._exit_with_error(exception)

        if notebooks:
            notebook = self.view.ask_for_notebook(notebooks)

            if not notebook:
                return

            path = self._db.get_notebook_by_title(notebook).path
            link = self._cloud.share_file(path.name)

            if link:
                self.view.show_info(link)
            else:
                self.view.show_info(f"Could not share '{path.name}'.")
        else:
            self.view.show_info('No notebooks found.')
