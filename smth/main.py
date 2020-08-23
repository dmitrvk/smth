# License: GNU GPL Version 3

"""smth main module."""

import argparse
import importlib.util
import logging
import sys

from smth import commands, const, db, view, __version__


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

    parser = argparse.ArgumentParser(prog='smth')

    parser.add_argument(
        '-v', '--version', action='store_true', help='print version and exit')

    subparsers = parser.add_subparsers(title='commands', metavar='')

    subparsers.add_parser(
        'create', aliases=['c'], help='create new notebook'
    ).set_defaults(func=create)

    subparsers.add_parser(
        'delete', aliases=['d'], help='delete notebook'
    ).set_defaults(func=delete)

    subparsers.add_parser(
        'list', aliases=['l'], help='show available notebooks'
    ).set_defaults(func=list_)

    subparsers.add_parser(
        'open', aliases=['o'], help='open notebook in default PDF viewer'
    ).set_defaults(func=open_)

    parser_scan = subparsers.add_parser(
        'scan', aliases=['s'], help='scan notebook')
    parser_scan.set_defaults(func=scan)

    scan_args_group = parser_scan.add_mutually_exclusive_group()

    scan_args_group.add_argument(
        '--set-device',
        help='choose scanning device',
        action='store_true')

    scan_args_group.add_argument(
        '--pdf-only',
        help='do not scan but only create PDF',
        action='store_true')

    subparsers.add_parser(
        'share', aliases=['sh'],
        help='share notebook uploaded to Google Drive (requires PyDrive)'
    ).set_defaults(func=share)

    parser_types = subparsers.add_parser(
        'types', aliases=['sh'], help='manage notebook types')
    parser_types.set_defaults(func=types)

    types_args_group = parser_types.add_mutually_exclusive_group()
    types_args_group.add_argument(
        '-c', '--create', action='store_true', help='create new type')
    types_args_group.add_argument(
        '-d', '--delete', action='store_true', help='delete type')

    subparsers.add_parser(
        'update', aliases=['up'],
        help="change notebook's title or path to PDF file"
    ).set_defaults(func=update)

    subparsers.add_parser(
        'upload', aliases=['u'],
        help='upload notebook to Google Drive (requires PyDrive)'
    ).set_defaults(func=upload)

    args = parser.parse_args()

    if args.version:
        print(__version__)
    elif hasattr(args, 'func'):
        args.func(args, db_, view_)
    else:
        args = parser.parse_args(['scan'])
        args.func(args, db_, view_)


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


def create(args, db_: db.DB, view_: view.View) -> None:
    """Runs `create` command."""
    commands.CreateCommand(db_, view_).execute(args)


def delete(args, db_: db.DB, view_: view.View) -> None:
    """Runs `delete` command."""
    commands.DeleteCommand(db_, view_).execute(args)


def list_(args, db_: db. DB, view_: view.View) -> None:
    """Runs `list` command."""
    commands.ListCommand(db_, view_).execute(args)


def open_(args, db_: db. DB, view_: view.View) -> None:
    """Runs `open` command."""
    commands.OpenCommand(db_, view_).execute(args)


def scan(args, db_: db. DB, view_: view.View) -> None:
    """Runs `scan` command."""
    commands.ScanCommand(db_, view_).execute(args)


def share(args, db_: db. DB, view_: view.View) -> None:
    """Runs `share` command."""
    if importlib.util.find_spec('pydrive'):
        commands.ShareCommand(db_, view_).execute(args)
    else:
        view_.show_info('PyDrive not found.')


def types(args, db_: db. DB, view_: view.View) -> None:
    """Runs `types` command."""
    commands.TypesCommand(db_, view_).execute(args)


def update(args, db_: db. DB, view_: view.View) -> None:
    """Runs `update` command."""
    commands.UpdateCommand(db_, view_).execute(args)


def upload(args, db_: db. DB, view_: view.View) -> None:
    """Runs `upload` command."""
    if importlib.util.find_spec('pydrive'):
        commands.UploadCommand(db_, view_).execute(args)
    else:
        view_.show_info('PyDrive not found.')
