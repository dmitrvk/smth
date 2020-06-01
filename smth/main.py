import logging
import os
import pathlib
import sys

from smth import controllers
from smth import views

DATA_ROOT = os.path.expanduser('~/.local/share/smth')

DB_PATH = os.path.join(DATA_ROOT, 'smth.db')

LOG_FILE = os.path.join(DATA_ROOT, 'smth.log')

PAGES_ROOT = os.path.join(DATA_ROOT, 'pages/')

HELP_MESSAGE = '''Syntax: `smth <command>`. Available commands:
    create      create new notebook
    list        show all available notebooks
    scan        scan notebook
    types       show all available notebook types'''

def main():
    if not os.path.exists(DATA_ROOT):
        pathlib.Path(DATA_ROOT).mkdir(parents=True, exist_ok=True)

    if not os.path.exists(PAGES_ROOT):
        pathlib.Path(PAGES_ROOT).mkdir(parents=True, exist_ok=True)

    setup_logging()
    log = logging.getLogger(__name__)

    view = views.BaseView()

    if len(sys.argv) == 2:
        command = sys.argv[1]

        if command == 'create':
            controllers.CreateController(DB_PATH).create_notebook()
        elif command == 'list':
            controllers.ListController(DB_PATH).show_notebooks_list()
        elif command == 'scan':
            controllers.ScanController(DB_PATH).scan_notebook()
        elif command == 'types':
            controllers.TypesController(DB_PATH).show_types_list()
        else:
            view.show_info(f"Unknown command '{command}'.")
            view.show_info(HELP_MESSAGE)
            log.info(f"Unknown command '{command}'")
    else:
        view.show_info(HELP_MESSAGE)
        log.info(f"Wrong args: '{sys.argv}'")

def setup_logging(filename=LOG_FILE, log_level=logging.DEBUG) -> None:
    log = logging.getLogger()
    log.setLevel(log_level)

    formatter = logging.Formatter(logging.BASIC_FORMAT)

    handler = logging.FileHandler(filename)
    handler.setLevel(log_level)
    handler.setFormatter(formatter)

    log.addHandler(handler)

