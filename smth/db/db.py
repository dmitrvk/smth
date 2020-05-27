import logging
import sqlite3
from typing import List

from .error import Error
from smth import models

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
    type_id INTEGER NOT NULL,
    path TEXT,
    total_pages INTEGER,
    first_page_number INTEGER,
    FOREIGN KEY(type_id) REFERENCES notebook_type(id))'''

SQL_GET_NOTEBOOKS = '''SELECT * FROM notebook ORDER BY title'''

SQL_GET_NOTEBOOK_TITLES = '''SELECT title FROM notebook ORDER BY title'''

SQL_NOTEBOOK_EXISTS = '''SELECT COUNT(*) FROM notebook WHERE title=?'''

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

SQL_CREATE_NOTEBOOK_TYPE = '''INSERT INTO
    notebook_type(title, page_width, page_height, pages_paired)
    VALUES(?, ?, ?, ?)'''

SQL_UPDATE_NOTEBOOK_TYPE = '''UPDATE notebook_type
    SET title=?, page_width=?, page_height=?, pages_paired=?
    WHERE id=?'''

SQL_GET_NOTEBOOK_BY_TITLE = '''SELECT * FROM notebook WHERE title=?'''

SQL_GET_NOTEBOOK_TYPES = '''SELECT * FROM notebook_type ORDER BY title'''

SQL_GET_NOTEBOOK_TYPE_TITLES = '''SELECT title FROM notebook_type
    ORDER BY title'''

SQL_GET_NOTEBOOK_TYPE_BY_ID = '''SELECT * FROM notebook_type WHERE id=?'''

SQL_GET_NOTEBOOK_TYPE_BY_TITLE = '''SELECT * FROM notebook_type
    WHERE title=?'''

SQL_NOTEBOOK_TYPE_EXISTS = '''SELECT COUNT(*) FROM notebook_type
    WHERE title=?'''


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
                notebook_type = self.get_type_by_id(row[2])
                notebook = models.Notebook(row[1], notebook_type, row[3])
                notebook.id = row[0]
                notebook.total_pages = row[4]
                notebook.first_page_number = row[5]
                notebooks.append(notebook)

        except (sqlite3.Error, Error) as e:
            self._handle_error('Failed to get notebooks from database', e)

        finally:
            if cursor != None:
                cursor.close()
            if connection != None:
                connection.close()

        return notebooks

    def get_notebook_by_title(self, title: int) -> models.Notebook:
        notebook = models.Notebook('', None, '')

        connection = None
        cursor = None

        try:
            connection = sqlite3.connect(self._path)
            cursor = connection.cursor()
            cursor.execute(SQL_GET_NOTEBOOK_BY_TITLE, (title,))
            row = cursor.fetchone()
            if row != None:
                title = row[1]
                type = self.get_type_by_id(row[2])
                path = row[3]

                notebook = models.Notebook(title, type, path)
                notebook.id = row[0]
                notebook.total_pages = row[4]
                notebook.first_page_number = row[5]

        except (sqlite3.Error, Error) as e:
            self._handle_error('Failed to get notebook type from database', e)

        finally:
            if cursor != None:
                cursor.close()
            if connection != None:
                connection.close()

        return notebook

    def get_notebook_titles(self) -> List[str]:
        """Return list of notebook titles from database."""
        titles = []

        connection = None
        cursor = None

        try:
            connection = sqlite3.connect(self._path)
            cursor = connection.cursor()
            cursor.execute(SQL_GET_NOTEBOOK_TITLES)

            titles = [row[0] for row in cursor]

        except sqlite3.Error as exception:
            self._handle_error(
                'Failed to get notebooks from database', exception)

        finally:
            if cursor != None:
                cursor.close()
            if connection != None:
                connection.close()

        return titles

    def get_types(self) -> list:
        types = []

        connection = None
        cursor = None

        try:
            connection = sqlite3.connect(self._path)
            cursor = connection.cursor()
            cursor.execute(SQL_GET_NOTEBOOK_TYPES)

            for row in cursor:
                type_ = models.NotebookType(row[1], row[2], row[3])
                types.append(type_)

        except sqlite3.Error as e:
            self._handle_error('Failed to get notebook types from database', e)

        finally:
            if cursor != None:
                cursor.close()
            if connection != None:
                connection.close()

        return types

    def get_type_titles(self) -> List[str]:
        """Return list of notebook types' titles from database."""
        titles = []

        connection = None
        cursor = None

        try:
            connection = sqlite3.connect(self._path)
            cursor = connection.cursor()
            cursor.execute(SQL_GET_NOTEBOOK_TYPE_TITLES)

            titles = [row[0] for row in cursor]

        except sqlite3.Error as exception:
            self._handle_error(
                'Failed to get notebooks from database', exception)

        finally:
            if cursor != None:
                cursor.close()
            if connection != None:
                connection.close()

        return titles

    def get_type_by_id(self, id: int) -> models.NotebookType:
        type_ = models.NotebookType('', 0, 0)

        connection = None
        cursor = None

        try:
            connection = sqlite3.connect(self._path)
            cursor = connection.cursor()
            cursor.execute(SQL_GET_NOTEBOOK_TYPE_BY_ID, (id,))
            row = cursor.fetchone()
            if row != None:
                type_.id = row[0]
                type_.title = row[1]
                type_.page_width = row[2]
                type_.page_height = row[3]

        except sqlite3.Error as e:
            self._handle_error('Failed to get notebook type from database', e)

        finally:
            if cursor != None:
                cursor.close()
            if connection != None:
                connection.close()

        return type_

    def get_type_by_title(self, title: str) -> models.NotebookType:
        type_ = models.NotebookType('', 0, 0)

        connection = None
        cursor = None

        try:
            connection = sqlite3.connect(self._path)
            cursor = connection.cursor()
            cursor.execute(SQL_GET_NOTEBOOK_TYPE_BY_TITLE, (title,))
            row = cursor.fetchone()
            if row != None:
                type_.id = row[0]
                type_.title = row[1]
                type_.page_width = row[2]
                type_.page_height = row[3]

        except sqlite3.Error as e:
            self._handle_error('Failed to get notebook type from database', e)

        finally:
            if cursor != None:
                cursor.close()
            if connection != None:
                connection.close()

        return type_

    def notebook_exists(self, title: str) -> bool:
        exists = False

        connection = None
        cursor = None

        try:
            connection = sqlite3.connect(self._path)
            cursor = connection.cursor()
            cursor.execute(SQL_NOTEBOOK_EXISTS, (title,))
            exists = cursor.fetchone()[0] > 0

        except sqlite3.Error as e:
            self._handle_error('Failed to check if notebook exists', e)

        finally:
            if cursor != None:
                cursor.close()
            if connection != None:
                connection.close()

        return exists

    def type_exists(self, title: str) -> bool:
        exists = False

        connection = None
        cursor = None

        try:
            connection = sqlite3.connect(self._path)
            cursor = connection.cursor()
            cursor.execute(SQL_NOTEBOOK_TYPE_EXISTS, (title,))
            exists = cursor.fetchone()[0] > 0

        except sqlite3.Error as e:
            self._handle_error('Failed to check if notebook type exists', e)

        finally:
            if cursor != None:
                cursor.close()
            if connection != None:
                connection.close()

        return exists

    def save_notebook(self, notebook: models.Notebook) -> None:
        """Create or update notebook."""
        connection = None

        try:
            connection = sqlite3.connect(self._path)

            if notebook.id < 0:
                values = (
                    notebook.title, notebook.type.title, notebook.path,
                    notebook.total_pages, notebook.first_page_number)
                connection.execute(SQL_CREATE_NOTEBOOK, values)
            else:
                values = (
                    notebook.title, notebook.type.title, notebook.path,
                    notebook.total_pages, notebook.first_page_number,
                    notebook.id)
                connection.execute(SQL_UPDATE_NOTEBOOK, values)

            connection.commit()

        except sqlite3.Error as e:
            self._handle_error('Failed to save notebook', e)

        finally:
            if connection:
                connection.close()

    def save_type(self, type: models.NotebookType) -> None:
        """Create or update notebook type."""
        connection = None

        try:
            connection = sqlite3.connect(self._path)

            if type.id < 0:
                values = (
                    type.title, type.page_width, type.page_height,
                    type.pages_paired)
                connection.execute(SQL_CREATE_NOTEBOOK_TYPE, values)
            else:
                values = (
                    type.title, type.page_width, type.page_height,
                    type.pages_paired, type.id)
                connection.execute(SQL_UPDATE_NOTEBOOK_TYPE, values)

            connection.commit()

        except sqlite3.Error as exception:
            self._handle_error('Failed to save notebook type', exception)
        finally:
            if connection:
                connection.close()

    def _handle_error(self, message: str, e: sqlite3.Error) -> None:
        """Log error message and propagate db.Error."""
        log.exception(message)
        raise Error(f'{message}: {e}.') from None

