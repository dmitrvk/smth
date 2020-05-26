import logging
import os
import pathlib
import sys
from time import sleep

import fpdf

from .db import DB
from .db_error import DBError
from .validators import NotebookValidator

log = logging.getLogger(__name__)


class BackupSystem:
    def __init__(self):
        try:
            self._db = DB()
            self._notebooks = self._db.get_notebooks()

            if not self._db.notebook_type_exists('A4'):
                self._db.create_notebook_type('A4', 210, 297, False)

            self._notebook_types = self._db.get_notebook_types()
        except DBError as e:
            self._print_exception(e)
            sys.exit(1)

    def list(self) -> None:
        """Print list of all notebooks or notebook types."""
        if self._notebooks != None and len(self._notebooks) > 0:
            print('All notebooks:')
            for notebook in self._notebooks:
                print(f'  {notebook.title}  {notebook.total_pages} pages  '
                    f'({notebook.type.title})')
        else:
            print('No notebooks found.')

    def create(self, title: str, type: str, path: str, first: int = 1) -> None:
        """Create notebook with given title, type, path and 1st page number."""
        try:
            title = str(title).strip()
            type = str(type).strip()
            path = self._expand_path(path)

            NotebookValidator(self._db).validate(title, type, path, first)

            self._create_empty_pdf(path)
            self._db.create_notebook(title, type, path, first)

            pages_dir = os.path.expanduser(f'~/.local/share/smth/pages/{title}/')
            pathlib.Path(pages_dir).mkdir(parents=True)

            log.info(f"Create notebook '{title}' of type '{type}' at '{path}'")
            print(f"Created notebook '{title}' of type '{type}' at '{path}'")

        except (DBError, OSError, ValueError) as e:
            self._print_exception(e)
            sys.exit(1)

    def types(self) -> None:
        """Print list of all notebook types."""
        if self._notebook_types != None and len(self._notebook_types) > 0:
            print('All notebook types:')
            for _type in self._notebook_types:
                print(f'  {_type.title}  '
                    f'{_type.page_width}x{_type.page_height}mm')
        else:
            print('No types found.')

    def _expand_path(self, path: str) -> str:
        """Return full absolute path."""
        path = str(path).strip()
        path = os.path.expandvars(os.path.expanduser(path))
        return os.path.abspath(path)

    def _create_empty_pdf(self, path: str) -> str:
        pdf = fpdf.FPDF()
        pdf.add_page()
        pdf.output(path)

    def _print_exception(self, exception: Exception):
        log.exception(exception)
        print(exception, file=sys.stderr)

