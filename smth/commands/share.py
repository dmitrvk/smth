import logging
from typing import List

from smth import db, cloud, view

from . import command

log = logging.getLogger(__name__)


class ShareCommand(command.Command):  # pylint: disable=too-few-public-methods
    """A command for sharing notebooks."""

    def __init__(self, db_: db.DB, view_: view.View):
        super().__init__(db_, view_)
        self._cloud = cloud.Cloud(ShareCommand.CloudCallback(self, view_))

    def execute(self, args: List[str] = None):
        """Share notebook and show a link."""
        try:
            notebooks = self._db.get_notebook_titles()
        except db.Error as exception:
            self.exit_with_error(exception)

        if notebooks:
            notebook = self.view.ask_for_notebook(notebooks)

            if not notebook:
                return

            path = self._db.get_notebook_by_title(notebook).path

            self._cloud.share_file(path.name)
        else:
            self.view.show_info('No notebooks found.')

    class CloudCallback(cloud.Callback):
        def __init__(self, command_: command.Command, view_: view.View):
            super().__init__()
            self._command = command_
            self._view = view_

        def on_start_sharing_file(self, filename: str) -> None:
            self._view.show_info(f"Sharing file '{filename}'...")

        def on_finish_sharing_file(self, filename: str, link: str) -> None:
            if link:
                self._view.show_info(f"Link to '{filename}': {link}")
            else:
                self.view.show_error(f"Could not share '{filename}'.")

        def on_error(self, message: str) -> None:
            self._command.exit_with_error(message)

        def on_start_uploading_file(self, path) -> None:
            pass

        def on_confirm_override_file(self, filename: str) -> bool:
            pass

        def on_finish_uploading_file(self, path) -> None:
            pass

        def on_create_smth_folder(self) -> None:
            pass
