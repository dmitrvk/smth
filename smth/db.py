# License: GNU GPL Version 3

"""This module provides an interface to the sqlite database.

    Typical usage example:

    try:
        db_ = db.DB('/path/to/sqlite.db')
        notebooks = db_.get_notebooks()

    except db.Error:
        pass
"""

import logging
import pathlib
import sqlite3
from typing import List

from smth import const, models

log = logging.getLogger(__name__)


class Error(Exception):
    """An error which occurs when working with the database."""


class DB:
    """Class used to perform operations with the database."""

    def __init__(self, path='smth.db'):
        """Create tables and the default notebook type if necessary.

        The default notebook type is of A4 format in portrait orientation.
        """
        self._path = path
        connection = None

        try:
            connection = self._connect()

            cursor = connection.execute(
                const.SQL_TABLE_EXISTS, ('notebook_type',))
            table_exists = cursor.fetchone()[0] > 0

            if not table_exists:
                connection.execute(const.SQL_CREATE_TABLE_NOTEBOOK_TYPE)
                log.info("Table 'notebook_type' created")

                type_a4 = models.NotebookType('A4', 210, 297)
                self.save_type(type_a4)
                log.info("Type 'A4' created")

            cursor = connection.execute(const.SQL_TABLE_EXISTS, ('notebook',))
            table_exists = cursor.fetchone()[0] > 0

            if not table_exists:
                connection.execute(const.SQL_CREATE_TABLE_NOTEBOOK)
                log.info("Table 'notebook' created")

            connection.commit()

        except sqlite3.Error as exception:
            self._handle_error(
                'Failed to initialize the database', exception)

        finally:
            if connection:
                connection.close()

    def get_notebooks(self) -> List[models.Notebook]:
        """Return all notebooks from the database.

        Raises:
            db.Error:
                An error occured executing the query.
        """
        notebooks = []
        connection = None

        try:
            connection = self._connect()
            for row in connection.execute(const.SQL_GET_NOTEBOOKS):
                notebooks.append(self._make_notebook_from_row(row))

        except (sqlite3.Error, Error) as exception:
            self._handle_error(
                'Failed to get notebooks from database', exception)

        finally:
            if connection:
                connection.close()

        return notebooks

    def get_notebook_by_title(self, title: str) -> models.Notebook:
        """Return notebook with specific title from database.

        Args:
            title:
                A title of a notebook.
        Raises:
            db.Error:
                An error occured executing the query.
        """
        notebook = models.Notebook(
            '', models.NotebookType('', 0, 0), pathlib.Path())

        connection = None

        try:
            connection = self._connect()
            cursor = connection.execute(
                const.SQL_GET_NOTEBOOK_BY_TITLE, (title,))
            row = cursor.fetchone()
            if row:
                notebook = self._make_notebook_from_row(row)

        except (sqlite3.Error, Error) as exception:
            self._handle_error(
                'Failed to get notebook from database', exception)

        finally:
            if connection:
                connection.close()

        return notebook

    def get_notebook_by_path(self, path: str) -> models.Notebook:
        """Return notebook with specific path from database.

        Args:
            path:
                A path to notebook's PDF file.
        Raises:
            db.Error:
                An error occured executing the query.
        """
        notebook = models.Notebook(
            '', models.NotebookType('', 0, 0), pathlib.Path())

        connection = None

        try:
            connection = self._connect()
            cursor = connection.execute(
                const.SQL_GET_NOTEBOOK_BY_PATH, (path,))
            row = cursor.fetchone()
            if row:
                notebook = self._make_notebook_from_row(row)

        except (sqlite3.Error, Error) as exception:
            self._handle_error(
                'Failed to get notebook from database', exception)

        finally:
            if connection:
                connection.close()

        return notebook

    def get_notebook_titles(self) -> List[str]:
        """Return list of notebook titles from database.

        Raises:
            db.Error:
                An error occured executing the query.
        """
        titles = []
        connection = None

        try:
            connection = self._connect()
            for row in connection.execute(const.SQL_GET_NOTEBOOK_TITLES):
                titles.append(row['title'])

        except sqlite3.Error as exception:
            self._handle_error(
                'Failed to get notebooks from database', exception)

        finally:
            if connection:
                connection.close()

        return titles

    def notebook_exists(self, title: str) -> bool:
        """Check if notebook with the given title exists in the database.

        Args:
            title:
                A title of a notebook.

        Raises:
            db.Error:
                An error occured executing the query.
        """
        exists = False
        connection = None

        try:
            connection = self._connect()
            cursor = connection.execute(const.SQL_NOTEBOOK_COUNT, (title,))
            exists = cursor.fetchone()[0] > 0

        except sqlite3.Error as exception:
            self._handle_error(
                'Failed to check if notebook exists', exception)

        finally:
            if connection:
                connection.close()

        return exists

    def notebooks_of_type_exist(self, type_title: str) -> bool:
        """Return true if there is one or more notebooks of the type.

        Args:
            type_title:
                A title of notebook's type.

        Raises:
            db.Error:
                An error occured executing the query.
        """
        exists = False
        connection = None

        try:
            connection = sqlite3.connect(self._path)

            cursor = connection.execute(
                const.SQL_NOTEBOOK_WITH_TYPE_COUNT, (type_title,))
            exists = cursor.fetchone()[0] > 0

        except sqlite3.Error as exception:
            self._handle_error(
                'Failed to check if notebooks of the type exist', exception)

        finally:
            if connection:
                connection.close()

        return exists

    def save_notebook(self, notebook: models.Notebook) -> None:
        """Create or update notebook.

        Args:
            notebook:
                A notebook to create or update.

        Raises:
            db.Error:
                An error occured executing the query.
        """
        connection = None

        try:
            connection = self._connect()

            if notebook.id < 0:
                values = (
                    notebook.title, notebook.type.title, str(notebook.path),
                    notebook.total_pages, notebook.first_page_number)
                connection.execute(const.SQL_CREATE_NOTEBOOK, values)
            else:
                values = (
                    notebook.title, notebook.type.title, str(notebook.path),
                    notebook.total_pages, notebook.first_page_number,
                    notebook.id)
                connection.execute(const.SQL_UPDATE_NOTEBOOK, values)

            connection.commit()

        except sqlite3.Error as exception:
            self._handle_error(
                'Failed to save notebook', exception)

        finally:
            if connection:
                connection.close()

    def delete_notebook_by_id(self, id_: int) -> None:
        """Delete notebook with the given id from the database.

        Args:
            id_:
                ID of notebook to delete.

        Raises:
            db.Error:
                An error occured executing the query.
        """
        connection = None

        try:
            connection = sqlite3.connect(self._path)
            connection.execute(const.SQL_DELETE_NOTEBOOK, (id_,))
            connection.commit()

        except sqlite3.Error as exception:
            self._handle_error('Failed to delete notebook', exception)

        finally:
            if connection:
                connection.close()

    def get_types(self) -> List[models.NotebookType]:
        """Return list of types from database.

        Raises:
            db.Error:
                An error occured executing the query.
        """
        types = []
        connection = None

        try:
            connection = self._connect()
            for row in connection.execute(const.SQL_GET_TYPES):
                types.append(self._make_type_from_row(row))

        except sqlite3.Error as exception:
            self._handle_error(
                'Failed to get notebook types from database', exception)

        finally:
            if connection:
                connection.close()

        return types

    def get_type_titles(self) -> List[str]:
        """Return list of notebook types' titles from database.

        Raises:
            db.Error:
                An error occured executing the query.
        """
        titles = []
        connection = None

        try:
            connection = self._connect()
            for row in connection.execute(const.SQL_GET_TYPE_TITLES):
                titles.append(row['title'])

        except sqlite3.Error as exception:
            self._handle_error(
                'Failed to get notebooks from database', exception)

        finally:
            if connection:
                connection.close()

        return titles

    def get_type_by_id(self, id_: int) -> models.NotebookType:
        """Return notebook type with specified id from database.

        Args:
            id_:
                A notebook type's ID.

        Raises:
            db.Error:
                An error occured executing the query.
        """
        type_ = models.NotebookType('', 0, 0)
        connection = None

        try:
            connection = self._connect()
            cursor = connection.execute(const.SQL_GET_TYPE_BY_ID, (id_,))
            row = cursor.fetchone()
            if row:
                type_ = self._make_type_from_row(row)

        except sqlite3.Error as exception:
            self._handle_error(
                'Failed to get notebook type from database', exception)

        finally:
            if connection:
                connection.close()

        return type_

    def get_type_by_title(self, title: str) -> models.NotebookType:
        """Return type with given title from the database.

        Args:
            title:
                A notebook type's title.

        Raises:
            db.Error:
                An error occured executing the query.
        """
        type_ = models.NotebookType('', 0, 0)
        connection = None

        try:
            connection = self._connect()
            cursor = connection.execute(const.SQL_GET_TYPE_BY_TITLE, (title,))
            row = cursor.fetchone()
            if row:
                type_ = self._make_type_from_row(row)

        except sqlite3.Error as exception:
            self._handle_error(
                'Failed to get notebook type from database', exception)

        finally:
            if connection:
                connection.close()

        return type_

    def type_exists(self, title: str) -> bool:
        """Check if type with the given title exists in the database.

        Args:
            title:
                A notebook type's title.

        Raises:
            db.Error:
                An error occured executing the query.
        """
        exists = False

        connection = None

        try:
            connection = self._connect()
            cursor = connection.execute(const.SQL_TYPE_COUNT, (title,))
            exists = cursor.fetchone()[0] > 0

        except sqlite3.Error as exception:
            self._handle_error(
                'Failed to check if notebook type exists', exception)

        finally:
            if connection:
                connection.close()

        return exists

    def save_type(self, type_: models.NotebookType) -> None:
        """Create or update notebook type.

        Args:
            type_:
                A notebook type to create or update.

        Raises:
            db.Error:
                An error occured executing the query.
        """
        connection = None

        try:
            connection = sqlite3.connect(self._path)

            if type_.id < 0:
                values = (
                    type_.title, type_.page_width, type_.page_height,
                    type_.pages_paired)
                connection.execute(const.SQL_CREATE_TYPE, values)
            else:
                values = (
                    type_.title, type_.page_width, type_.page_height,
                    type_.pages_paired, type_.id)
                connection.execute(const.SQL_UPDATE_TYPE, values)

            connection.commit()

        except sqlite3.Error as exception:
            self._handle_error('Failed to save notebook type', exception)

        finally:
            if connection:
                connection.close()

    def delete_type_by_title(self, title: str) -> None:
        """Delete type with the given title from the database.

        Args:
            title:
                A notebook type's title.

        Raises:
            db.Error:
                An error occured executing the query.
        """
        connection = None

        try:
            connection = sqlite3.connect(self._path)
            connection.execute(const.SQL_DELETE_TYPE_BY_TITLE, (title,))
            connection.commit()

        except sqlite3.Error as exception:
            self._handle_error('Failed to delete notebook type', exception)

        finally:
            if connection:
                connection.close()

    def _connect(self) -> sqlite3.Connection:
        """Connect to the database and return the connection object.

        Raises:
            sqlite3.Error:
                Error when connection failed.
        """
        connection = sqlite3.connect(self._path)
        connection.row_factory = sqlite3.Row
        return connection

    def _handle_error(self, message: str, error: Exception) -> None:  # pylint: disable=no-self-use  # noqa: E501
        """Log error message and propagate db.Error."""
        log.exception(message)
        raise Error(f'{message}: {error}.') from None

    def _make_notebook_from_row(self, row: sqlite3.Row) -> models.Notebook:
        type_ = self.get_type_by_id(row['type_id'])
        notebook = models.Notebook(
            row['title'], type_, pathlib.Path(row['path']))
        notebook.id = row['id']
        notebook.total_pages = row['total_pages']
        notebook.first_page_number = row['first_page_number']
        return notebook

    def _make_type_from_row(self, row: sqlite3.Row) -> models.NotebookType:  # pylint: disable=no-self-use  # noqa: E501
        type_ = models.NotebookType(
            row['title'], row['page_width'], row['page_height'])
        type_.id = row['id']
        type_.pages_paired = row['pages_paired'] > 0
        return type_
