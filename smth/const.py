# License: GNU GPL Version 3

"""The module contains some constants that are used across other modules."""

import pathlib

CONFIG_PATH = pathlib.Path('~/.config/smth/smth.conf').expanduser()

DATA_ROOT_PATH = pathlib.Path('~/.local/share/smth').expanduser()

DB_PATH = DATA_ROOT_PATH / 'smth.db'

LOG_PATH = DATA_ROOT_PATH / 'smth.log'

PAGES_ROOT_PATH = DATA_ROOT_PATH / 'pages/'

HELP_MESSAGE = '''Syntax: `smth <command>`. Available commands:
    create      create new notebook
    delete      delete notebook
    list        show all available notebooks
    open        open notebook in default PDF viewer
    scan        scan notebook
    share       share notebook uploaded to Google Drive (requires PyDrive)
    types       show all available notebook types
    update      change notebook's title or path to PDF file
    upload      upload notebook to Google Drive (requires PyDrive)'''
