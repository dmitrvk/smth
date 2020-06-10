import logging
import pathlib
import sys

from smth import db, config, commands, view

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

    view_ = view.View()

    try:
        db_ = db.DB(DB_PATH)
    except db.Error as exception:
        view_.show_error(str(exception))
        log.exception(exception)
        sys.exit(1)

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'create':
            commands.CreateCommand(db_, view_).execute()
        elif command == 'list':
            commands.ListCommand(db_, view_).execute()
        elif command == 'scan':
            commands.ScanCommand(db_, view_, conf).execute(sys.argv[2:])
        elif command == 'types':
            commands.TypesCommand(db_, view_).execute()
        else:
            view_.show_info(f"Unknown command '{command}'.")
            view_.show_info(HELP_MESSAGE)
            log.info(f"Unknown command '{command}'")
    else:
        view_.show_info(HELP_MESSAGE)
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
