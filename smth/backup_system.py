import logging
import sys
from time import sleep

from .db import DB

log = logging.getLogger(__name__)


class BackupSystem:
    def __init__(self):
        try:
            self._db = DB()
        except Exception as e:
            self._print_except('Failed to initialize the database', e)
            sys.exit(1)

        try:
            self._notebooks = self._db.get_notebooks()
        except Exception as e:
            self._print_except('Failed to get notebooks from database', e)
            sys.exit(1)

        try:
            self._notebook_types = self._db.get_notebook_types()
        except Exception as e:
            self._print_except('Failed to get notebook types from database', e)
            sys.exit(1)

    def _print_except(self, message, e):
        print(f'{message}: {e}.', file=sys.stderr)
        log.exception(message)

