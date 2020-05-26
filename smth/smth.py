import logging
import os
import pathlib
import sys

from smth.backup_system import BackupSystem
from smth.view import View

LOG_FILE = os.path.expanduser('~/.local/share/smth/smth.log')

PAGES_ROOT = os.path.expanduser('~/.local/share/smth/pages/')

HELP_MESSAGE = '''Syntax: `smth <command>`. Available commands:
    create      create new notebook
    list        show all available notebooks
    scan        scan notebook
    types       show all available notebook types'''

def main():
    setup_logging()

    if not os.path.exists(PAGES_ROOT):
        pathlib.Path(PAGES_ROOT).mkdir(parents=True, exist_ok=True)

    view = View()
    backup_system = BackupSystem(view)

    if len(sys.argv) == 2:
        command = getattr(backup_system, sys.argv[1], None)
        if callable(command):
            command()
        else:
            view.show_info(HELP_MESSAGE)
    else:
        view.show_info(HELP_MESSAGE)

def setup_logging(filename=LOG_FILE, log_level=logging.DEBUG) -> None:
    log = logging.getLogger()
    log.setLevel(log_level)
    handler = logging.FileHandler(filename)
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    log.addHandler(handler)

