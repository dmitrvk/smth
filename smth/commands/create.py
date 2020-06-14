import logging
import os
import pathlib
from typing import List

import fpdf

from smth import db, models, validators

from . import command

log = logging.getLogger(__name__)


class CreateCommand(command.Command):  # pylint: disable=too-few-public-methods
    """Creates a new notebook."""

    def execute(self, args: List[str] = None) -> None:
        """Ask user for new notebook info, save notebook in the database.


        If path to PDF ends with '.pdf', it is treated as a file.  That allows
        user to specify custom name for notebook's file.  Otherwise, treat the
        path as a directory.  The file will be stored in that directory.
        If the directory does not exist, create it with all parent directories.
        """
        try:
            types = self._db.get_type_titles()
            validator = validators.NotebookValidator(self._db)

            answers = self.view.ask_for_new_notebook_info(types, validator)

            if not answers:
                log.info('Creation stopped due to keyboard interrupt')
                self.view.show_info('Nothing created.')
                return

            title = answers['title']
            type_ = self._db.get_type_by_title(answers['type'])
            path = pathlib.Path(
                os.path.expandvars(answers['path'])).expanduser().resolve()

            if str(path).endswith('.pdf'):
                if not path.parent.exists():
                    path.parent.mkdir(parents=True, exist_ok=True)
            else:
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)
                path = path / f'{title}.pdf'

            notebook = models.Notebook(title, type_, path)
            notebook.first_page_number = answers['first_page_number']

            pdf = fpdf.FPDF()
            pdf.add_page()
            pdf.output(path)
            log.info("Created empty PDF at '{path}'")

            self._db.save_notebook(notebook)

            pages_root = os.path.expanduser('~/.local/share/smth/pages')
            pages_dir = os.path.join(pages_root, notebook.title)
            pathlib.Path(pages_dir).mkdir(parents=True)

            message = (f"Create notebook '{notebook.title}' "
                       f"of type '{notebook.type.title}' at '{notebook.path}'")
            log.info(message)
            self.view.show_info(message)
        except db.Error as exception:
            self._exit_with_error(exception)
