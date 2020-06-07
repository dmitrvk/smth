import logging
import os
import pathlib
import sys

import fpdf

from smth import db, models, views
from smth.controllers import validators

log = logging.getLogger(__name__)


class CreateController:
    """Creates a new notebook."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_notebook(self) -> None:
        """Ask user for new notebook info, save notebook in the database."""
        view = views.CreateView()

        try:
            db_ = db.DB(self.db_path)
            types = db_.get_type_titles()
            validator = validators.NotebookValidator(db_)

            answers = view.ask_for_new_notebook_info(types, validator)

            if not answers:
                log.info('Creation stopped due to keyboard interrupt')
                view.show_info('Nothing created.')
                return

            title = answers['title'].strip()
            type = db_.get_type_by_title(answers['type'].strip())
            path = self._expand_path(answers['path'])

            if path.endswith('.pdf'):
                dir = os.path.dirname(path)
                if not os.path.exists(dir):
                    pathlib.Path(dir).mkdir(parents=True)
            else:
                if not os.path.exists(path):
                    pathlib.Path(path).mkdir(parents=True)
                path = os.path.join(path, f'{title}.pdf')

            notebook = models.Notebook(title, type, path)
            notebook.first_page_number = int(answers['first_page_number'])

            self._create_empty_pdf(notebook.path)

            db_.save_notebook(notebook)

            pages_root = os.path.expanduser('~/.local/share/smth/pages')
            pages_dir = os.path.join(pages_root, notebook.title)
            pathlib.Path(pages_dir).mkdir(parents=True)

            message = (f"Create notebook '{notebook.title}' "
                       f"of type '{notebook.type.title}' at '{notebook.path}'")
            log.info(message)
            view.show_info(message)
        except db.Error as exception:
            log.exception(exception)
            view.show_error(str(exception))
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
