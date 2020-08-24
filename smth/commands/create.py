# License: GNU GPL Version 3

"""The module provides `create` command for creating notebooks."""

import argparse
import logging
import os
import pathlib

import fpdf

from smth import db, models, validators

from . import command, types

log = logging.getLogger(__name__)


class CreateCommand(command.Command):  # pylint: disable=too-few-public-methods
    """Creates a new notebook."""

    def execute(self, args: argparse.Namespace) -> None:
        """Asks user for new notebook info, saves notebook in the database.

        If path to PDF ends with '.pdf', it is treated as a file.  That allows
        user to specify custom name for notebook's file.  Otherwise, treat the
        path as a directory.  The file will be stored in that directory.
        If the directory does not exist, create it with all parent directories.
        """
        try:
            type_titles = self._db.get_type_titles()

        except db.Error as exception:
            self.exit_with_error(exception)

        if not type_titles:
            self._view.show_info("No types found. Please, create a new one:")
            self._view.show_separator()
            types.TypesCommand(self._db, self._view).execute(['--create'])

            type_titles = self._db.get_type_titles()

            if type_titles:
                self._view.show_separator()
                self._view.show_info('Creating a new notebook:')
            else:
                self.exit_with_error("No types found. Create one with "
                                     "'smth types --create'.")

        validator = validators.NotebookValidator(self._db)

        answers = self._view.ask_for_new_notebook_info(type_titles, validator)

        if not answers:
            log.info('Creation stopped due to keyboard interrupt')
            self._view.show_info('Nothing created.')
            return

        title = answers['title']

        try:
            type_ = self._db.get_type_by_title(answers['type'])

        except db.Error as exception:
            self.exit_with_error(exception)

        path = pathlib.Path(
            os.path.expandvars(answers['path'])).expanduser().resolve()

        if str(path).endswith('.pdf'):
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
        else:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)

            path = path / f'{title}.pdf'

            if path.exists():
                message = ("Notebook not created because "
                           f"'{path}' already exists.")
                self.exit_with_error(message)

        notebook = models.Notebook(title, type_, path)
        notebook.first_page_number = answers['first_page_number']

        pdf = fpdf.FPDF()
        pdf.add_page()

        try:
            pdf.output(path)
            log.info("Created empty PDF at '{path}'")

            self._db.save_notebook(notebook)

        except (OSError, db.Error) as exception:
            self.exit_with_error(exception)

        pages_root = os.path.expanduser('~/.local/share/smth/pages')
        pages_dir = os.path.join(pages_root, notebook.title)
        pathlib.Path(pages_dir).mkdir(parents=True)

        message = (f"Create notebook '{notebook.title}' "
                   f"of type '{notebook.type.title}' at '{notebook.path}'")
        log.info(message)
        self._view.show_info(message)
