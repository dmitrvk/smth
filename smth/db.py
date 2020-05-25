import logging
import sqlite3

from .db_error import DBError
from .notebook import Notebook
from .notebook_type import NotebookType


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

SQL_GET_NOTEBOOKS = '''SELECT * FROM notebook ORDER BY title'''

SQL_GET_NOTEBOOK_TYPES = '''SELECT * FROM notebook_type ORDER BY title'''

SQL_GET_NOTEBOOK_TYPE_BY_ID = '''SELECT * FROM notebook_type WHERE id=?'''


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

        except sqlite3.Error as e:
            self._handle_error('Failed to initialize the database', e)

        finally:
            if connection != None:
                connection.close()

    def get_notebooks(self) -> list:
        notebooks = []

        connection = None
        cursor = None

        try:
            connection = sqlite3.connect(self._path)
            cursor = connection.cursor()
            cursor.execute(SQL_GET_NOTEBOOKS)

            for row in cursor:
                notebook_type = self.get_notebook_type_by_id(row[2])
                notebook = Notebook(row[1], notebook_type, row[3])
                notebooks.append(notebook)

        except sqlite3.Error as exception:
            self._handle_error('Failed to get notebooks from database', e)

        finally:
            if cursor != None:
                cursor.close()
            if connection != None:
                connection.close()

        return notebooks

    def get_notebook_types(self) -> list:
        notebook_types = []

        connection = None
        cursor = None

        try:
            connection = sqlite3.connect(self._path)
            cursor = connection.cursor()
            cursor.execute(SQL_GET_NOTEBOOK_TYPES)

            for row in cursor:
                notebook_type = NotebookType(row[1], row[2], row[3])
                notebook_types.append(notebook_type)

        except sqlite3.Error as e:
            self._handle_error('Failed to get notebook types from database', e)

        finally:
            if cursor != None:
                cursor.close()
            if connection != None:
                connection.close()

        return notebook_types

    def get_notebook_type_by_id(self, id: int) -> NotebookType:
        notebook_type = NotebookType('', 0, 0)

        connection = None
        cursor = None

        try:
            connection = sqlite3.connect(self._path)
            cursor = connection.cursor()
            cursor.execute(SQL_GET_NOTEBOOK_TYPE_BY_ID, (id,))
            row = cursor.fetchone()
            if row != None:
                notebook_type.title = row[1]
                notebook_type.page_width = row[2]
                notebook_type.page_height = row[3]

        except sqlite3.Error as e:
            self._handle_error('Failed to get notebook type from database', e)

        finally:
            if cursor != None:
                cursor.close()
            if connection != None:
                connection.close()

        return notebook_type

    def _handle_error(self, message: str, e: sqlite3.Error) -> None:
        """Log error message and propagate DBError."""
        log.exception(message)
        raise DBError(f'{message}: {e}.') from None
