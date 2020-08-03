# License: GNU GPL Version 3

"""The module provides `open` command for openning notebook in PDF viewer."""

import logging
import subprocess
from typing import List

from . import command

log = logging.getLogger(__name__)


class OpenCommand(command.Command):  # pylint: disable=too-few-public-methods
    """A command which can be executed with arguments."""

    def execute(self, args: List[str] = None):
        """Open notebook's PDF file in default viewer."""
        notebook_titles = self.get_notebook_titles_from_db()

        if not notebook_titles:
            self.view.show_info('No notebooks found.')
        else:
            notebook = self.view.ask_for_notebook(notebook_titles)

            if notebook:
                path = self._db.get_notebook_by_title(notebook).path
                subprocess.Popen(['xdg-open', str(path)])
