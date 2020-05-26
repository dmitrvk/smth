import logging
import os
import pathlib
import sys

from smth.backup_system import BackupSystem

LOG_FILE = os.path.expanduser('~/.local/share/smth/smth.log')

PAGES_ROOT = os.path.expanduser('~/.local/share/smth/pages/')

def main():
    setup_logging()

    if not os.path.exists(PAGES_ROOT):
        pathlib.Path(PAGES_ROOT).mkdir(parents=True, exist_ok=True)

    backup_system = BackupSystem()

    if len(sys.argv) == 2:
        command = getattr(backup_system, sys.argv[1], None)
        if callable(command):
            command()
        else:
            print('Syntax: `smth <command>`. Available commands: create, list, types')
    else:
        print('Syntax: `smth <command>`. Available commands: create, list, types')

def setup_logging(filename=LOG_FILE, log_level=logging.DEBUG) -> None:
    log = logging.getLogger()
    log.setLevel(log_level)
    handler = logging.FileHandler(filename)
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    log.addHandler(handler)

