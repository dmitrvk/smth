"""smth main module."""

import importlib.util
import logging
import pathlib
import sys

from smth import commands, config, db, view

DATA_ROOT = pathlib.Path('~/.local/share/smth').expanduser()

DB_PATH = DATA_ROOT / 'smth.db'

LOG_PATH = DATA_ROOT / 'smth.log'

PAGES_ROOT = DATA_ROOT / 'pages/'

HELP_MESSAGE = '''Syntax: `smth <command>`. Available commands:
    create      create new notebook
    list        show all available notebooks
    open        open notebook in default PDF viewer
    scan        scan notebook
    share       share notebook uploaded to Google Drive (requires PyDrive)
    types       show all available notebook types
    upload      upload notebook to Google Drive (requires PyDrive)'''


def main():
    """Create needed files, initialize logs, database, view.

    Parse arguments and run command that user specified.
    Show help if no command provided or specified command is invalid."""
    if not DATA_ROOT.exists():
        DATA_ROOT.mkdir(parents=True, exist_ok=True)

    if not PAGES_ROOT.exists():
        PAGES_ROOT.mkdir(parents=True, exist_ok=True)

    setup_logging()
    log = logging.getLogger(__name__)

    view_ = view.View()

    try:
        conf = config.Config()
    except config.Error as exception:
        view_.show_error(f'{exception}.')
        log.exception(exception)
        sys.exit(1)

    try:
        db_ = db.DB(DB_PATH)
    except db.Error as exception:
        view_.show_error(f'{exception}.')
        log.exception(exception)
        sys.exit(1)

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'create':
            commands.CreateCommand(db_, view_).execute()
        elif command == 'list':
            commands.ListCommand(db_, view_).execute()
        elif command == 'open':
            commands.OpenCommand(db_, view_).execute()
        elif command == 'scan':
            commands.ScanCommand(db_, view_, conf).execute(sys.argv[2:])
        elif command == 'share':
            if importlib.util.find_spec('pydrive'):
                commands.ShareCommand(db_, view_).execute()
            else:
                view_.show_info('PyDrive not found.')
        elif command == 'types':
            commands.TypesCommand(db_, view_).execute(sys.argv[2:])
        elif command == 'upload':
            if importlib.util.find_spec('pydrive'):
                commands.UploadCommand(db_, view_).execute()
            else:
                view_.show_info('PyDrive not found.')
        else:
            view_.show_info(f"Unknown command '{command}'.")
            view_.show_info(HELP_MESSAGE)
            log.info("Unknown command '%s'", command)
    else:
        commands.ScanCommand(db_, view_, conf).execute(sys.argv[2:])


def setup_logging(log_level=logging.DEBUG) -> None:
    """Set logging file, level, format."""
    log = logging.getLogger()
    log.setLevel(log_level)

    format_ = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
    formatter = logging.Formatter(format_)

    handler = logging.FileHandler(str(LOG_PATH))
    handler.setLevel(log_level)
    handler.setFormatter(formatter)

    log.addHandler(handler)
