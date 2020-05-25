import logging
import sys
from time import sleep

from .db import DB
from .db_error import DBError

log = logging.getLogger(__name__)


class BackupSystem:
    def __init__(self):
        try:
            self._db = DB()
            self._notebooks = self._db.get_notebooks()
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

    def types(self) -> None:
        """Print list of all notebook types."""
        if self._notebook_types != None and len(self._notebook_types) > 0:
            print('All notebook types:')
            for _type in self._notebook_types:
                print(f'  {_type.title}  '
                    f'{_type.page_width}x{_type.page_height}mm')
        else:
            print('No types found.')

    def _print_exception(self, exception: Exception):
        log.exception(exception)
        print(exception, file=sys.stderr)

