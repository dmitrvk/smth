import logging
import subprocess
from typing import List

from smth import db

from . import command

log = logging.getLogger(__name__)


class OpenCommand(command.Command):  # pylint: disable=too-few-public-methods
    """A command which can be executed with arguments."""

    def execute(self, args: List[str] = None):
        """Open notebook's PDF file in default viewer."""
        try:
            notebooks = self._db.get_notebook_titles()
        except db.Error as exception:
            self.exit_with_error(exception)

        if notebooks:
            notebook = self.view.ask_for_notebook(notebooks)

            if notebook:
                path = self._db.get_notebook_by_title(notebook).path
                subprocess.Popen(['xdg-open', str(path)])
        else:
            self.view.show_info('No notebooks found.')
