import logging
import os
import pathlib
import sys

import fpdf

from smth import commands, db, models, view
from smth import validators

log = logging.getLogger(__name__)


class CreateCommand(commands.Command):
    """Creates a new notebook."""

    def __init__(self, db_: db.DB, view_: view.View):
        self.db = db_
        self.view = view_

    def execute(self) -> None:
        """Ask user for new notebook info, save notebook in the database."""
        try:
            types = self.db.get_type_titles()
            validator = validators.NotebookValidator(self.db)

            answers = self.view.ask_for_new_notebook_info(types, validator)

            if not answers:
                log.info('Creation stopped due to keyboard interrupt')
                self.view.show_info('Nothing created.')
                return

            title = answers['title'].strip()
            type_ = self.db.get_type_by_title(answers['type'].strip())
            path = self._expand_path(answers['path'])

            if path.endswith('.pdf'):
                dir_ = os.path.dirname(path)
                if not os.path.exists(dir_):
                    pathlib.Path(dir_).mkdir(parents=True)
            else:
                if not os.path.exists(path):
                    pathlib.Path(path).mkdir(parents=True)
                path = os.path.join(path, f'{title}.pdf')

            notebook = models.Notebook(title, type_, path)
            notebook.first_page_number = int(answers['first_page_number'])

            self._create_empty_pdf(notebook.path)

            self.db.save_notebook(notebook)

            pages_root = os.path.expanduser('~/.local/share/smth/pages')
            pages_dir = os.path.join(pages_root, notebook.title)
            pathlib.Path(pages_dir).mkdir(parents=True)

            message = (f"Create notebook '{notebook.title}' "
                       f"of type '{notebook.type.title}' at '{notebook.path}'")
            log.info(message)
            self.view.show_info(message)
        except db.Error as exception:
            log.exception(exception)
            self.view.show_error(str(exception))
            sys.exit(1)

    def _expand_path(self, path: str) -> str:
        """Return full absolute path."""
        path = str(path).strip()
        path = os.path.expandvars(os.path.expanduser(path))
        return os.path.abspath(path)

    def _create_empty_pdf(self, path: str) -> None:
        pdf = fpdf.FPDF()
        pdf.add_page()
        pdf.output(path)
        log.info("Created empty PDF at '{path}'")
