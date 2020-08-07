# License: GNU GPL Version 3

"""The module provides `upload` command for uploading notebooks to cloud."""

import logging
import pathlib
from typing import List

from smth import cloud, db, view

from . import command

log = logging.getLogger(__name__)


class UploadCommand(command.Command):  # pylint: disable=too-few-public-methods  # noqa: E501
    """A command for uploading notebooks to Google Drive."""

    def __init__(self, db_: db.DB, view_: view.View):
        super().__init__(db_, view_)
        self._cloud = cloud.Cloud(UploadCommand.CloudCallback(self, view_))

    def execute(self, args: List[str] = None):
        """Uploads a notebook's PDF file to Google Drive."""
        notebook_titles = self.get_notebook_titles_from_db()

        if notebook_titles:
            path = None

            if args:
                notebook_title = args[0]

                for title in notebook_titles:
                    if title == notebook_title:
                        try:
                            path = self._db.get_notebook_by_title(title).path
                            self._cloud.upload_file(path)
                            return
                        except db.Error as exception:
                            self.exit_with_error(exception)

            if not path:
                notebook = self._view.ask_for_notebook(notebook_titles)

                if notebook:
                    path = self._db.get_notebook_by_title(notebook).path
                    self._cloud.upload_file(path)
        else:
            self._view.show_info('No notebooks found.')

    class CloudCallback(cloud.UploadingCallback):
        """Callback implementation to subscribe on cloud's events."""

        def __init__(self, command_: command.Command, view_: view.View):
            super().__init__()
            self._command = command_
            self._view = view_

        def on_start_uploading_file(self, path: pathlib.Path) -> None:
            """See the base class."""
            message = "Uploading '{}' to Google Drive...".format(str(path))
            self._view.show_info(message)

        def on_confirm_overwrite_file(self, filename: str) -> bool:
            """See the base class."""
            question = f"File '{filename}' exists on Google Drive. Override?"
            return self._view.confirm(question)

        def on_finish_uploading_file(self, path: pathlib.Path) -> None:
            """See the base class."""
            message = f"File '{path.name}' uploaded to Google Drive."
            self._view.show_info(message)

        def on_create_smth_folder(self) -> None:
            """See the base class."""
            self._view.show_info("Folder 'smth' created on Google Drive.")

        def on_error(self, message: str) -> None:
            """See the base class."""
            self._command.exit_with_error(message)
