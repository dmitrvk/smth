import logging
import pathlib
import sys

from smth import config, controllers, views

DATA_ROOT = pathlib.Path('~/.local/share/smth').expanduser()

CONFIG_PATH = pathlib.Path('~/.config/smth/smth.conf').expanduser()

DB_PATH = DATA_ROOT / 'smth.db'

LOG_PATH = DATA_ROOT / 'smth.log'

PAGES_ROOT = DATA_ROOT / 'pages/'

HELP_MESSAGE = '''Syntax: `smth <command>`. Available commands:
    create      create new notebook
    list        show all available notebooks
    scan        scan notebook
    types       show all available notebook types'''


def main():
    if not DATA_ROOT.exists():
        DATA_ROOT.mkdir(parents=True, exist_ok=True)

    if not PAGES_ROOT.exists():
        PAGES_ROOT.mkdir(parents=True, exist_ok=True)

    setup_logging()
    log = logging.getLogger(__name__)

    conf = config.Config()

    view = views.BaseView()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'create':
            controllers.CreateController(str(DB_PATH)).create_notebook()
        elif command == 'list':
            controllers.ListController(str(DB_PATH)).show_notebooks_list()
        elif command == 'scan':
            controllers.ScanController(
                sys.argv[2:], str(DB_PATH), conf).scan_notebook()
        elif command == 'types':
            controllers.TypesController(str(DB_PATH)).show_types_list()
        else:
            view.show_info(f"Unknown command '{command}'.")
            view.show_info(HELP_MESSAGE)
            log.info(f"Unknown command '{command}'")
    else:
        view.show_info(HELP_MESSAGE)
        log.info(f"Wrong args: '{sys.argv}'")


def setup_logging(log_level=logging.DEBUG) -> None:
    log = logging.getLogger()
    log.setLevel(log_level)

    format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
    formatter = logging.Formatter(format)

    handler = logging.FileHandler(str(LOG_PATH))
    handler.setLevel(log_level)
    handler.setFormatter(formatter)

    log.addHandler(handler)
