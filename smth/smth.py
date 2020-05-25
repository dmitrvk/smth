import logging

import fire
import os
import pathlib

from .backup_system import BackupSystem

PAGES_ROOT = os.path.expanduser('~/.local/share/smth/pages/')

def main():
    setup_logging()

    if not os.path.exists(PAGES_ROOT):
        pathlib.Path(PAGES_ROOT).mkdir(parents=True, exist_ok=True)

    fire.Fire(BackupSystem)

def setup_logging(filename='smth.log', log_level=logging.DEBUG) -> None:
    log = logging.getLogger()
    log.setLevel(log_level)
    handler = logging.FileHandler(filename)
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    log.addHandler(handler)

