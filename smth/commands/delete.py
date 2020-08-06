# License: GNU GPL Version 3

"""The module provides `delete` command for deleting notebooks."""

import logging
import pathlib
import shutil
from typing import List

from smth import db

from . import command

log = logging.getLogger(__name__)


class DeleteCommand(command.Command):  # pylint: disable=too-few-public-methods
    """Deletes a notebook."""

    def execute(self, args: List[str] = None) -> None:
        """Asks for notebook, removes it from db, but leaves PDF untouched."""
        try:
            notebook_titles = self.get_notebook_titles_from_db()

            if not notebook_titles:
                self._view.show_info('No notebooks found.')
                return

            chosen_notebook = self._view.ask_for_notebook(notebook_titles)

            if not chosen_notebook:
                log.info('Deletion stopped due to keyboard interrupt')
                return

            notebook = self._db.get_notebook_by_title(chosen_notebook)

            pages_root = pathlib.Path('~/.local/share/smth/pages').expanduser()
            pages_dir_path = pages_root / notebook.title

            message = (f"All scanned images in '{pages_dir_path}' will be "
                       f"removed.\n"
                       f"File'{notebook.path}' will not be deleted.")
            self._view.show_info(message)

            if self._view.confirm('Continue?'):
                self._db.delete_notebook_by_id(notebook.id)

                if pages_dir_path.exists():
                    shutil.rmtree(str(pages_dir_path))

                message = (f"Notebook '{notebook.title}' deleted.")
                log.info(message)
                self._view.show_info(message)
        except db.Error as exception:
            self.exit_with_error(exception)
