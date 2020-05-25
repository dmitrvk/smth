import logging

import fire

from .backup_system import BackupSystem

def main():
    setup_logging()
    fire.Fire(BackupSystem)

def setup_logging(filename='smth.log', log_level=logging.DEBUG) -> None:
    log = logging.getLogger()
    log.setLevel(log_level)
    handler = logging.FileHandler(filename)
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    log.addHandler(handler)

