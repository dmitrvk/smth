import logging
import sqlite3

log = logging.getLogger(__name__)

SQL_CREATE_TABLE_NOTEBOOK_TYPE = '''CREATE TABLE IF NOT EXISTS notebook_type(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE,
    page_width INTEGER,
    page_height INTEGER,
    pages_paired INTEGER)'''

SQL_CREATE_TABLE_NOTEBOOK = '''CREATE TABLE IF NOT EXISTS notebook(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE,
    notebook_type_id INTEGER,
    path TEXT,
    total_pages INTEGER,
    first_page_number INTEGER,
    FOREIGN KEY(notebook_type_id) REFERENCES notebook_type(id))'''


class DB:
    def __init__(self, path='smth.db'):
        self._path = path

        connection = None

        try:
            connection = sqlite3.connect(path)
            connection.execute(SQL_CREATE_TABLE_NOTEBOOK_TYPE)
            connection.commit()
            connection.execute(SQL_CREATE_TABLE_NOTEBOOK)
            connection.commit()
            log.info('Created tables if they did not exist')
        except sqlite3.Error as exception:
            log.exception('Failed to create tables')
            raise exception
        finally:
            if connection != None:
                connection.close()

