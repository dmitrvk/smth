# License: GNU GPL Version 3

"""The module provides `types` command for managing notebook types."""

import logging
from typing import List

from smth import db, models, validators

from . import command

log = logging.getLogger(__name__)


class TypesCommand(command.Command):  # pylint: disable=too-few-public-methods
    """Displays the list of all notebooks."""

    def execute(self, args: List[str] = None) -> None:
        """Gets notebook types from database and shows them to user.

        If `--create` option is passed, asks user for new type info and
        saves new type in the database.
        """
        if args and '--create' in args:
            self._create_type()
        elif args and '--delete' in args:
            self._delete_type()
        else:
            try:
                types = self._db.get_types()
                self._view.show_types(types)
            except db.Error as exception:
                self.exit_with_error(exception)

    def _create_type(self):
        """Asks for the information about new type and saves it in database."""
        validator = validators.TypeValidator(self._db)
        answers = self._view.ask_for_new_type_info(validator)

        if not answers:
            log.info('Type creation stopped due to keyboard interrupt')
            self._view.show_info('Nothing created.')
            return

        type_ = models.NotebookType(
            answers['title'],
            answers['page_width'],
            answers['page_height'])
        type_.pages_paired = answers['pages_paired']

        try:
            self._db.save_type(type_)
        except db.Error as exception:
            self.exit_with_error(exception)

        message = (f"Created type '{type_.title}' "
                   f"{type_.page_width}x{type_.page_height}mm")

        if type_.pages_paired:
            message += " with paired pages"

        self._view.show_info(f'{message}.')
        log.info(message)

    def _delete_type(self):
        """Asks for type and deletes it from the database."""
        try:
            type_titles = self._db.get_type_titles()
        except db.Error as exception:
            self.exit_with_error(exception)

        type_title = self._view.ask_for_type(type_titles)

        if not type_title:
            return

        try:
            if self._db.notebooks_of_type_exist(type_title):
                self._view.show_info(
                    f"Can not delete type '{type_title}' because notebooks "
                    "of this type exist.")
            else:
                self._db.delete_type_by_title(type_title)
                self._view.show_info(f"Type '{type_title}' deleted.")

        except db.Error as exception:
            self.exit_with_error(exception)
