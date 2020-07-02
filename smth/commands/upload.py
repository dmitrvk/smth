import logging
from typing import List

from smth import commands, db

log = logging.getLogger(__name__)


class UploadCommand(commands.Command):  # pylint: disable=too-few-public-methods  # noqa: E501
    """A command which can be executed with arguments."""

    def execute(self, args: List[str] = None):
        """Upload notebook's PDF file to Google Drive."""
        try:
            import pydrive.auth  # noqa: F401
            import pydrive.drive  # noqa: F401
        except ImportError:
            self._exit_with_error('PyDrive not found.')

        try:
            notebooks = self._db.get_notebook_titles()
        except db.Error as exception:
            self._exit_with_error(exception)

        if notebooks:
            notebook = self.view.ask_for_notebook(notebooks)

            if notebook:
                path = self._db.get_notebook_by_title(notebook).path
                self.view.show_info(f"File '{path}' should be uploaded to Google Drive here.")  # noqa: E501
                self.view.show_info('This feature will be implemented in future versions')  # noqa: E501
        else:
            self.view.show_info('No notebooks found.')
