# License: GNU GPL Version 3

"""The module contains some constants that are used across other modules."""

import pathlib

CONFIG_PATH = pathlib.Path('~/.config/smth/smth.conf').expanduser()

DATA_ROOT_PATH = pathlib.Path('~/.local/share/smth').expanduser()

DB_PATH = DATA_ROOT_PATH / 'smth.db'

LOG_PATH = DATA_ROOT_PATH / 'smth.log'

PAGES_ROOT_PATH = DATA_ROOT_PATH / 'pages/'

SQL_CREATE_TABLE_NOTEBOOK_TYPE = '''CREATE TABLE IF NOT EXISTS notebook_type(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE,
    page_width INTEGER,
    page_height INTEGER,
    pages_paired INTEGER)'''

SQL_CREATE_TABLE_NOTEBOOK = '''CREATE TABLE IF NOT EXISTS notebook(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE,
    type_id INTEGER NOT NULL,
    path TEXT,
    total_pages INTEGER,
    first_page_number INTEGER,
    FOREIGN KEY(type_id) REFERENCES notebook_type(id))'''

SQL_TABLE_EXISTS = '''SELECT COUNT(*) FROM sqlite_master
    WHERE type='table' AND name=?'''

SQL_GET_NOTEBOOKS = '''SELECT * FROM notebook ORDER BY title'''

SQL_GET_NOTEBOOK_TITLES = '''SELECT title FROM notebook ORDER BY title'''

SQL_NOTEBOOK_COUNT = '''SELECT COUNT(*) FROM notebook WHERE title=?'''

SQL_NOTEBOOK_WITH_TYPE_COUNT = '''SELECT COUNT(*) FROM notebook, notebook_type
    WHERE notebook.type_id=notebook_type.id AND notebook_type.title=?'''

SQL_CREATE_NOTEBOOK = '''INSERT INTO
    notebook(title, type_id, path, total_pages, first_page_number)
    VALUES(?,
    (SELECT id FROM notebook_type WHERE title=?),
    ?, ?, ?)'''

SQL_UPDATE_NOTEBOOK = '''UPDATE notebook
    SET title=?,
    type_id=(SELECT id FROM notebook_type WHERE title=?),
    path=?, total_pages=?, first_page_number=?
    WHERE id=?'''

SQL_DELETE_NOTEBOOK = '''DELETE FROM notebook WHERE id=?'''

SQL_DELETE_TYPE_BY_TITLE = '''DELETE FROM notebook_type WHERE title=?'''

SQL_CREATE_TYPE = '''INSERT INTO
    notebook_type(title, page_width, page_height, pages_paired)
    VALUES(?, ?, ?, ?)'''

SQL_UPDATE_TYPE = '''UPDATE notebook_type
    SET title=?, page_width=?, page_height=?, pages_paired=?
    WHERE id=?'''

SQL_GET_NOTEBOOK_BY_TITLE = '''SELECT * FROM notebook WHERE title=?'''

SQL_GET_NOTEBOOK_BY_PATH = '''SELECT * FROM notebook WHERE path=?'''

SQL_GET_TYPES = '''SELECT * FROM notebook_type ORDER BY title'''

SQL_GET_TYPE_TITLES = '''SELECT title FROM notebook_type ORDER BY title'''

SQL_GET_TYPE_BY_ID = '''SELECT * FROM notebook_type WHERE id=?'''

SQL_GET_TYPE_BY_TITLE = '''SELECT * FROM notebook_type WHERE title=?'''

SQL_TYPE_COUNT = '''SELECT COUNT(*) FROM notebook_type WHERE title=?'''
