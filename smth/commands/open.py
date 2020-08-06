# License: GNU GPL Version 3

"""The module provides `open` command for openning notebook in PDF viewer."""

import logging
import subprocess
from typing import List

from . import command

log = logging.getLogger(__name__)


class OpenCommand(command.Command):  # pylint: disable=too-few-public-methods
    """Opens a notebook's PDF file in the default viewer."""

    def execute(self, args: List[str] = None):
        """See the base class."""
        notebook_titles = self.get_notebook_titles_from_db()

        if not notebook_titles:
            self._view.show_info('No notebooks found.')
        else:
            notebook = self._view.ask_for_notebook(notebook_titles)

            if notebook:
                path = self._db.get_notebook_by_title(notebook).path
                subprocess.Popen(['xdg-open', str(path)])
