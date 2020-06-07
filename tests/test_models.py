import unittest
from unittest import mock

from smth import models


class TestNotebook(unittest.TestCase):
    """Notebook model tests."""
    def setUp(self):
        self.notebook = models.Notebook('title', None, 'path')

    def test_id(self):
        self.notebook.id = 1
        self.assertEqual(self.notebook.id, 1)

    def test_title(self):
        self.assertEqual(models.Notebook('Test', None, 'path').title, 'Test')
        self.assertEqual(models.Notebook('', None, 'path').title, 'Untitled')

    def test_type(self):
        type = mock.MagicMock()
        notebook = models.Notebook('title', type, 'path')
        self.assertIs(notebook.type, type)
        with self.assertRaises(AttributeError):
            notebook.type = type

    def test_path(self):
        self.assertEqual(models.Notebook('', None, '/path.pdf').path, '/path.pdf')
        self.notebook.path = '/test/path/to/file.pdf'
        self.assertEqual(self.notebook.path, '/test/path/to/file.pdf')

    def test_total_pages(self):
        notebook = models.Notebook('title', None, 'path')

        self.assertEqual(notebook.total_pages, 0)

        notebook.total_pages = 10
        self.assertEqual(notebook.total_pages, 10)

        notebook.total_pages = 0
        self.assertEqual(notebook.total_pages, 0)

        notebook.total_pages = -10
        self.assertEqual(notebook.total_pages, 0)

    def test_first_page_number(self):
        self.assertEqual(self.notebook.first_page_number, 1)

        self.notebook.first_page_number = 0
        self.assertEqual(self.notebook.first_page_number, 0)

        self.notebook.first_page_number = 10
        self.assertEqual(self.notebook.first_page_number, 10)

        self.notebook.first_page_number = -10
        self.assertEqual(self.notebook.first_page_number, 1)

    def test__repr__(self):
        type = mock.MagicMock()
        type.title = 'Test Type'
        notebook = models.Notebook('Test', type, 'path')
        expected =  "<Notebook 'Test' of type 'Test Type'>"
        self.assertEqual(notebook.__repr__(), expected)


class TestNotebookType(unittest.TestCase):
    """NotebookType model tests."""

    def setUp(self):
        self.type_ = models.NotebookType('Test', 100, 200)

    def test_id(self):
        self.type_.id = 1
        self.assertEqual(self.type_.id, 1)

    def test_title(self):
        type_ = models.NotebookType('', 100, 200)
        self.assertEqual(type_.title, 'Untitled')

        type_.title = 'Test'
        self.assertEqual(type_.title, 'Test')

        type_.title = None
        self.assertEqual(type_.title, 'Untitled')

    def test_page_size(self):
        self.assertEqual(self.type_.page_width, 100)
        self.assertEqual(self.type_.page_height, 200)

        self.type_.page_width = -100
        self.type_.page_height = -200

        self.assertEqual(self.type_.page_width, 0)
        self.assertEqual(self.type_.page_height, 0)

    def test_pages_paired(self):
        self.assertEqual(self.type_.pages_paired, False)

        self.type_.pages_paired = True
        self.assertEqual(self.type_.pages_paired, True)

        self.type_.pages_paired = 'not a bool value'
        self.assertEqual(self.type_.pages_paired, False)

    def test__repr__(self):
        expected = "<NotebookType 'Test' of size 100x200mm>"
        self.assertEqual(self.type_.__repr__(), expected)

        self.type_.pages_paired = True

        expected = "<NotebookType 'Test' of size 100x200mm with paired pages>"
        self.assertEqual(self.type_.__repr__(), expected)
