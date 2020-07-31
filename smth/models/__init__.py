# License: GNU GPL Version 3

"""The package provides Notebook and Notebook Type models.

Notebook is a collection of pages ordered by their numbers.
Notebook is what the user scans: book, sheets with handwriting etc.
Each notebook has type, a unique name and path to PDF file.

Notebook type defines the size of a notebook's pages and whether pages are
paired.  This information is essential when rotating, cropping, and merging
scanned images.

    Typical usage example:

    type = models.NotebookType('A4', 210, 297)
    path = pathlib.Path('/path/to/file.pdf')

    notebook = models.Notebook('title', type, path)
"""

from .notebook import Notebook
from .notebook_type import NotebookType

__all__ = ['Notebook', 'NotebookType']
