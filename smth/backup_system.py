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

    def _print_exception(self, exception: Exception):
        log.exception(exception)
        print(exception, file=sys.stderr)

