import logging
import os
import pathlib
from typing import List

from smth import db

from . import command

log = logging.getLogger(__name__)


class UpdateCommand(command.Command):  # pylint: disable=too-few-public-methods
    """Update a notebook."""

    def execute(self, args: List[str] = None) -> None:
        """Ask user for notebook properties, save notebook in the database.

        Works similar to `create` command but changes the existing notebook."""
        try:
            notebook_titles = self._db.get_notebook_titles()
        except db.Error as exception:
            self.exit_with_error(exception)

        if not notebook_titles:
            self.view.show_info('No notebooks found.')
            return

        notebook_title = self.view.ask_for_notebook(notebook_titles)

        if not notebook_title:
            return

        try:
            notebook = self._db.get_notebook_by_title(notebook_title)
            types = self._db.get_type_titles()
        except db.Error as exception:
            self.exit_with_error(exception)

        answers = self.view.ask_for_updated_notebook_properties(
            notebook, types)

        if not answers:
            log.info('Update stopped due to keyboard interrupt')
            self.view.show_info('Nothing updated.')
            return

        title = answers['title']
        type_ = self._db.get_type_by_title(answers['type'])
        path = pathlib.Path(
            os.path.expandvars(answers['path'])).expanduser().resolve()

        print(title)
        print(type_)
        print(path)
        print(answers['first_page_number'])
        return
