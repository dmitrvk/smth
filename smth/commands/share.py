# License: GNU GPL Version 3

"""The module provides `share` command to share notebooks uploaded to cloud."""

import logging
from typing import List

from smth import cloud, db, view

from . import command

log = logging.getLogger(__name__)


class ShareCommand(command.Command):  # pylint: disable=too-few-public-methods
    """A command for sharing notebooks."""

    def __init__(self, db_: db.DB, view_: view.View):
        super().__init__(db_, view_)
        self._cloud = cloud.Cloud(ShareCommand.CloudCallback(self, view_))

    def execute(self, args: List[str] = None):
        """Shares a notebook and shows a link."""
        notebook_titles = self.get_notebook_titles_from_db()

        if not notebook_titles:
            self._view.show_info('No notebooks found.')
        else:
            notebook = self._view.ask_for_notebook(notebook_titles)

            if notebook:
                path = None

                try:
                    path = self._db.get_notebook_by_title(notebook).path
                except db.Error as exception:
                    self.exit_with_error(exception)

                if path:
                    self._cloud.share_file(path.name)

    class CloudCallback(cloud.SharingCallback):
        """Callback implementation to subscribe on cloud's events."""

        def __init__(self, command_: command.Command, view_: view.View):
            super().__init__()
            self._command = command_
            self._view = view_

        def on_start_sharing_file(self, filename: str) -> None:
            """See the base class."""
            self._view.show_info(f"Sharing file '{filename}'...")

        def on_finish_sharing_file(self, filename: str, link: str) -> None:
            """See the base class."""
            if link:
                self._view.show_info(f"Link to '{filename}': {link}")
            else:
                self._view.show_error(f"Could not share '{filename}'.")

        def on_create_smth_folder(self) -> None:
            """See the base class."""
            self._view.show_info("Folder 'smth' created on Google Drive.")

        def on_error(self, message: str) -> None:
            """See the base class."""
            self._command.exit_with_error(message)
