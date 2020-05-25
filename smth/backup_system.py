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
            print(f'Failed to initialize the database: {e}.')
            log.exception('Failed to initialize the database')
            sys.exit(1)

        try:
            self._notebooks = self._db.get_notebooks()
        except Exception as e:
            print(f'Failed to get notebooks from the database: {e}.')
            log.exception('Failed to get notebooks from the database')
            sys.exit(1)


