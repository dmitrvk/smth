import logging
import sqlite3
from typing import List

from smth import models


class Error(Exception):
    """An error which occurs when working with a database."""
    pass


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

SQL_TABLE_EXISTS = '''SELECT COUNT(*) FROM sqlite_master
    WHERE type='table' AND name=?'''

SQL_GET_NOTEBOOKS = '''SELECT * FROM notebook ORDER BY title'''

SQL_GET_NOTEBOOK_TITLES = '''SELECT title FROM notebook ORDER BY title'''

SQL_NOTEBOOK_COUNT = '''SELECT COUNT(*) FROM notebook WHERE title=?'''

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

SQL_CREATE_TYPE = '''INSERT INTO
    notebook_type(title, page_width, page_height, pages_paired)
    VALUES(?, ?, ?, ?)'''

SQL_UPDATE_TYPE = '''UPDATE notebook_type
    SET title=?, page_width=?, page_height=?, pages_paired=?
    WHERE id=?'''

SQL_GET_NOTEBOOK_BY_TITLE = '''SELECT * FROM notebook WHERE title=?'''

SQL_GET_TYPES = '''SELECT * FROM notebook_type ORDER BY title'''

SQL_GET_TYPE_TITLES = '''SELECT title FROM notebook_type ORDER BY title'''

SQL_GET_TYPE_BY_ID = '''SELECT * FROM notebook_type WHERE id=?'''

SQL_GET_TYPE_BY_TITLE = '''SELECT * FROM notebook_type WHERE title=?'''

SQL_TYPE_COUNT = '''SELECT COUNT(*) FROM notebook_type WHERE title=?'''


class DB:
    def __init__(self, path='smth.db'):
        """Create tables and default notebook type if necessary."""
        self._path = path
        connection = None

        try:
            connection = self._connect()

            cursor = connection.execute(SQL_TABLE_EXISTS, ('notebook_type',))
            table_exists = cursor.fetchone()[0] > 0

            if not table_exists:
                connection.execute(SQL_CREATE_TABLE_NOTEBOOK_TYPE)
                log.info("Table 'notebook_type' created")

                typeA4 = models.NotebookType('A4', 210, 297)
                self.save_type(typeA4)
                log.info("Type 'A4' created")

            cursor = connection.execute(SQL_TABLE_EXISTS, ('notebook',))
            table_exists = cursor.fetchone()[0] > 0

            if not table_exists:
                connection.execute(SQL_CREATE_TABLE_NOTEBOOK)
                log.info("Table 'notebook' created")

            connection.commit()

        except sqlite3.Error as e:
            self._handle_error('Failed to initialize the database', e)

        finally:
            if connection:
                connection.close()

    def get_notebooks(self) -> List[models.Notebook]:
        notebooks = []
        connection = None

        try:
            connection = self._connect()
            for row in connection.execute(SQL_GET_NOTEBOOKS):
                notebooks.append(self._make_notebook_from_row(row))

        except (sqlite3.Error, Error) as e:
            self._handle_error('Failed to get notebooks from database', e)

        finally:
            if connection:
                connection.close()

        return notebooks

    def get_notebook_by_title(self, title: int) -> models.Notebook:
        """Return notebook with specific title from database."""
        notebook = models.Notebook('', None, '')

        connection = None

        try:
            connection = self._connect()
            cursor = connection.execute(SQL_GET_NOTEBOOK_BY_TITLE, (title,))
            row = cursor.fetchone()
            if row:
                notebook = self._make_notebook_from_row(row)

        except (sqlite3.Error, Error) as e:
            self._handle_error('Failed to get notebook type from database', e)

        finally:
            if connection:
                connection.close()

        return notebook

    def get_notebook_titles(self) -> List[str]:
        """Return list of notebook titles from database."""
        titles = []
        connection = None

        try:
            connection = self._connect()
            for row in connection.execute(SQL_GET_NOTEBOOK_TITLES):
                titles.append(row['title'])

        except sqlite3.Error as e:
            self._handle_error('Failed to get notebooks from database', e)

        finally:
            if connection:
                connection.close()

        return titles

    def get_types(self) -> List[models.NotebookType]:
        """Return list of types from database."""
        types = []
        connection = None

        try:
            connection = self._connect()
            for row in connection.execute(SQL_GET_TYPES):
                types.append(self._make_type_from_row(row))

        except sqlite3.Error as e:
            self._handle_error('Failed to get notebook types from database', e)

        finally:
            if connection:
                connection.close()

        return types

    def get_type_titles(self) -> List[str]:
        """Return list of notebook types' titles from database."""
        titles = []
        connection = None

        try:
            connection = self._connect()
            for row in connection.execute(SQL_GET_TYPE_TITLES):
                titles.append(row['title'])

        except sqlite3.Error as e:
            self._handle_error('Failed to get notebooks from database', e)

        finally:
            if connection:
                connection.close()

        return titles

    def get_type_by_id(self, id: int) -> models.NotebookType:
        """Return notebook type with specified id from database."""
        type_ = models.NotebookType('', 0, 0)
        connection = None

        try:
            connection = self._connect()
            cursor = connection.execute(SQL_GET_TYPE_BY_ID, (id,))
            row = cursor.fetchone()
            if row:
                type_ = self._make_type_from_row(row)

        except sqlite3.Error as e:
            self._handle_error('Failed to get notebook type from database', e)

        finally:
            if connection:
                connection.close()

        return type_

    def get_type_by_title(self, title: str) -> models.NotebookType:
        type_ = models.NotebookType('', 0, 0)
        connection = None

        try:
            connection = self._connect()
            cursor = connection.execute(SQL_GET_TYPE_BY_TITLE, (title,))
            row = cursor.fetchone()
            if row:
                type_ = self._make_type_from_row(row)

        except sqlite3.Error as e:
            self._handle_error('Failed to get notebook type from database', e)

        finally:
            if connection:
                connection.close()

        return type_

    def notebook_exists(self, title: str) -> bool:
        exists = False
        connection = None

        try:
            connection = self._connect()
            cursor = connection.execute(SQL_NOTEBOOK_COUNT, (title,))
            exists = cursor.fetchone()[0] > 0

        except sqlite3.Error as e:
            self._handle_error('Failed to check if notebook exists', e)

        finally:
            if connection:
                connection.close()

        return exists

    def type_exists(self, title: str) -> bool:
        exists = False

        connection = None

        try:
            connection = self._connect()
            cursor = connection.execute(SQL_TYPE_COUNT, (title,))
            exists = cursor.fetchone()[0] > 0

        except sqlite3.Error as e:
            self._handle_error('Failed to check if notebook type exists', e)

        finally:
            if connection:
                connection.close()

        return exists

    def save_notebook(self, notebook: models.Notebook) -> None:
        """Create or update notebook."""
        connection = None

        try:
            connection = self._connect()

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
                connection.execute(SQL_CREATE_TYPE, values)
            else:
                values = (
                    type.title, type.page_width, type.page_height,
                    type.pages_paired, type.id)
                connection.execute(SQL_UPDATE_TYPE, values)

            connection.commit()

        except sqlite3.Error as exception:
            self._handle_error('Failed to save notebook type', exception)
        finally:
            if connection:
                connection.close()

    def _connect(self) -> sqlite3.Connection:
        """Connect to the database and return the connection object.

        Raises sqlite3.Error if connection failed."""
        connection = sqlite3.connect(self._path)
        connection.row_factory = sqlite3.Row
        return connection

    def _handle_error(self, message: str, e: sqlite3.Error) -> None:
        """Log error message and propagate db.Error."""
        log.exception(message)
        raise Error(f'{message}: {e}.') from None

    def _make_notebook_from_row(self, row: sqlite3.Row) -> models.Notebook:
        type_ = self.get_type_by_id(row['type_id'])
        notebook = models.Notebook(row['title'], type_, row['path'])
        notebook.id = row['id']
        notebook.total_pages = row['total_pages']
        notebook.first_page_number = row['first_page_number']
        return notebook

    def _make_type_from_row(self, row: sqlite3.Row) -> models.NotebookType:
        type_ = models.NotebookType(
            row['title'], row['page_width'], row['page_height'])
        type_.id = row['id']
        type_.pages_paired = row['pages_paired'] > 0
        return type_