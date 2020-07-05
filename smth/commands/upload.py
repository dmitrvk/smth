import logging
from typing import List

from smth import db, cloud, view

from . import command

log = logging.getLogger(__name__)


class UploadCommand(command.Command):  # pylint: disable=too-few-public-methods  # noqa: E501
    """A command for uploading notebooks to Google Drive."""

    def __init__(self, db_: db.DB, view_: view.View, cloud_: cloud.Cloud):
        super().__init__(db_, view_)
        self._cloud = cloud_

    def execute(self, args: List[str] = None):
        """Upload notebook's PDF file to Google Drive."""
        try:
            notebooks = self._db.get_notebook_titles()
        except db.Error as exception:
            self._exit_with_error(exception)

        if notebooks:
            notebook = self.view.ask_for_notebook(notebooks)

            if not notebook:
                return

            path = self._db.get_notebook_by_title(notebook).path

            self._cloud.upload_file(path)

            self.view.show_info(
                f"File '{path.name}' uploaded to Google Drive.")
        else:
            self.view.show_info('No notebooks found.')
