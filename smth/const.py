# License: GNU GPL Version 3

"""The module contains some constants that are used across other modules."""

import pathlib

CONFIG_PATH = pathlib.Path('~/.config/smth/smth.conf').expanduser()

DATA_ROOT_PATH = pathlib.Path('~/.local/share/smth').expanduser()

DB_PATH = DATA_ROOT_PATH / 'smth.db'

LOG_PATH = DATA_ROOT_PATH / 'smth.log'

PAGES_ROOT_PATH = DATA_ROOT_PATH / 'pages/'
