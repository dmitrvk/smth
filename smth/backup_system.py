import logging

from .db import DB

log = logging.getLogger(__name__)


class BackupSystem:
    def __init__(self):
        try:
            self._db = DB()
        except Exception as e:
            print(f'Failed to initialize the database: {e}.')
            log.exception('Failed to initialize the database.')

