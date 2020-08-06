# License: GNU GPL Version 3

"""smth main module."""

import importlib.util
import logging
import sys

from smth import commands, const, db, view


def main():
    """Creates needed files and initializes logs, database and view.

    Parses arguments and runs a command.
    Shows help message if no command provided or command is invalid."""
    if not const.DATA_ROOT_PATH.exists():
        const.DATA_ROOT_PATH.mkdir(parents=True, exist_ok=True)

    if not const.PAGES_ROOT_PATH.exists():
        const.PAGES_ROOT_PATH.mkdir(parents=True, exist_ok=True)

    if not const.CONFIG_PATH.parent.exists():
        const.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    setup_logging()
    log = logging.getLogger(__name__)

    view_ = view.View()

    try:
        db_ = db.DB(const.DB_PATH)
    except db.Error as exception:
        view_.show_error(f'{exception}.')
        log.exception(exception)
        sys.exit(1)

    def execute_command(command_name: str) -> None:
        command_class = f'{command_name.capitalize()}Command'
        command = getattr(commands, command_class)(db_, view_)
        command.execute(sys.argv[2:])

    if len(sys.argv) == 1:
        execute_command('scan')  # Default command
    else:
        command: str = sys.argv[1]

        if command in ('share', 'upload'):
            if importlib.util.find_spec('pydrive'):
                execute_command(command)
            else:
                view_.show_info('PyDrive not found.')

        elif command in (
                'create', 'delete', 'list', 'open', 'scan', 'types', 'update'):
            execute_command(command)

        else:
            view_.show_info(f"Unknown command '{command}'.")
            view_.show_info(const.HELP_MESSAGE)
            log.info("Unknown command '%s'", command)


def setup_logging() -> None:
    """Set logging file, level, format."""
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    format_ = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
    formatter = logging.Formatter(format_)

    handler = logging.FileHandler(str(const.LOG_PATH))
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    log.addHandler(handler)
