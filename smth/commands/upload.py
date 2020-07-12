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
        """Upload notebook's PDF file to Google Drive."""
        try:
            notebooks = self._db.get_notebook_titles()
        except db.Error as exception:
            self.exit_with_error(exception)

        if notebooks:
            path = None

            if args:
                notebook_title = args[0]

                for title in notebooks:
                    if title == notebook_title:
                        try:
                            path = self._db.get_notebook_by_title(title).path
                            self._cloud.upload_file(path)
                            return
                        except db.Error as exception:
                            self.exit_with_error(exception)

            if not path:
                notebook = self.view.ask_for_notebook(notebooks)

                if notebook:
                    path = self._db.get_notebook_by_title(notebook).path
                    self._cloud.upload_file(path)
        else:
            self.view.show_info('No notebooks found.')

    class CloudCallback(cloud.UploadingCallback):
        def __init__(self, command_: command.Command, view_: view.View):
            super().__init__()
            self._command = command_
            self._view = view_

        def on_start_uploading_file(self, path: pathlib.Path) -> None:
            message = "Uploading '{}' to Google Drive...".format(str(path))
            self._view.show_info(message)

        def on_confirm_override_file(self, filename: str) -> bool:
            question = f"File '{filename}' exists on Google Drive. Override?"
            return self._view.confirm(question)

        def on_finish_uploading_file(self, path: pathlib.Path) -> None:
            message = f"File '{path.name}' uploaded to Google Drive."
            self._view.show_info(message)

        def on_create_smth_folder(self) -> None:
            self._view.show_info("Folder 'smth' created on Google Drive.")

        def on_error(self, message: str) -> None:
            self._command.exit_with_error(message)
