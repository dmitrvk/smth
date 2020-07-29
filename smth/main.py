"""smth main module."""

import importlib.util
import logging
import sys

from smth import commands, const, config, db, view


def main():
    """Create needed files, initialize logs, database, view.

    Parse arguments and run command that user specified.
    Show help if no command provided or specified command is invalid."""
    if not const.DATA_ROOT_PATH.exists():
        const.DATA_ROOT_PATH.mkdir(parents=True, exist_ok=True)

    if not const.PAGES_ROOT_PATH.exists():
        const.PAGES_ROOT_PATH.mkdir(parents=True, exist_ok=True)

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
        db_ = db.DB(const.DB_PATH)
    except db.Error as exception:
        view_.show_error(f'{exception}.')
        log.exception(exception)
        sys.exit(1)

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'create':
            commands.CreateCommand(db_, view_).execute()
        elif command == 'delete':
            commands.DeleteCommand(db_, view_).execute()
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
        elif command == 'update':
            commands.UpdateCommand(db_, view_).execute(sys.argv[2:])
        elif command == 'upload':
            if importlib.util.find_spec('pydrive'):
                commands.UploadCommand(db_, view_).execute()
            else:
                view_.show_info('PyDrive not found.')
        else:
            view_.show_info(f"Unknown command '{command}'.")
            view_.show_info(const.HELP_MESSAGE)
            log.info("Unknown command '%s'", command)
    else:
        commands.ScanCommand(db_, view_, conf).execute(sys.argv[2:])


def setup_logging(log_level=logging.DEBUG) -> None:
    """Set logging file, level, format."""
    log = logging.getLogger()
    log.setLevel(log_level)

    format_ = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
    formatter = logging.Formatter(format_)

    handler = logging.FileHandler(str(const.LOG_PATH))
    handler.setLevel(log_level)
    handler.setFormatter(formatter)

    log.addHandler(handler)
