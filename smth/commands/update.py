# License: GNU GPL Version 3

"""The module provides `update` command for changing notebook's properties."""

import logging
import os
import pathlib
import shutil
from typing import List

from smth import db, validators

from . import command

log = logging.getLogger(__name__)


class UpdateCommand(command.Command):  # pylint: disable=too-few-public-methods
    """Update a notebook."""

    def execute(self, args: List[str] = None) -> None:  # pylint: disable=too-many-branches  # noqa: E501
        """Asks user for notebook properties, saves notebook in the database.

        Works similar to `create` command but changes the existing notebook.
        """
        notebook_titles = self.get_notebook_titles_from_db()

        if not notebook_titles:
            self._view.show_info('No notebooks found.')
            return

        notebook_title = self._view.ask_for_notebook(notebook_titles)

        if not notebook_title:
            return

        try:
            notebook = self._db.get_notebook_by_title(notebook_title)
        except db.Error as exception:
            self.exit_with_error(exception)

        validator = validators.NotebookUpdateValidator()

        answers = self._view.ask_for_updated_notebook_properties(
            notebook, validator)

        if not answers:
            log.info('Update stopped due to keyboard interrupt')
            self._view.show_info('Nothing updated.')
            return

        title = answers['title']
        path = pathlib.Path(
            os.path.expandvars(answers['path'])).expanduser().resolve()

        if title != notebook.title:
            if self._db.notebook_exists(title):
                message = ("Error: Notebook with title "
                           f"'{title}' already exists.")
                self.exit_with_error(message)

        if path != notebook.path:
            if not str(path).endswith('.pdf'):
                path = path / f'{title}.pdf'

            if path.exists():
                message = (f"Error: '{path}' already exists.")
                self.exit_with_error(message)

            try:
                existing_notebook = self._db.get_notebook_by_path(str(path))
            except db.Error as exception:
                self.exit_with_error(exception)

            if existing_notebook.title != 'Untitled':
                message = (f"Error: '{path}' already taken "
                           f"by notebook '{existing_notebook.title}'.")
                self.exit_with_error(message)

            if not path.parent.exists():
                path.mkdir(parents=True, exist_ok=True)

            if notebook.path.exists():
                shutil.move(str(notebook.path), str(path))

            notebook.path = path

        if title != notebook.title:
            pages_root = pathlib.Path(
                '~/.local/share/smth/pages').expanduser()
            pages_dir = pages_root / notebook.title
            new_pages_dir = pages_root / title
            shutil.move(str(pages_dir), str(new_pages_dir))

            notebook.title = title

        self._db.save_notebook(notebook)

        self._view.show_info('Notebook saved.')
