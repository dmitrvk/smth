import logging
import operator
import os
import sqlite3
import unittest
from unittest import mock

from smth import db, models


class TestDB(unittest.TestCase):
    """Test database operations."""

    DB_PATH = 'smth-test.db'

    def setUp(self):
        self.db = db.DB(self.DB_PATH)

        # Types for tests
        self.types = self.db.get_types()
        type1 = models.NotebookType('Type 1', 100, 200)
        type2 = models.NotebookType('Type 2', 200, 100)
        type2.pages_paired = True
        self.types.append(type1)
        self.types.append(type2)
        for type in self.types:
            self.db.save_type(type)

        # Notebooks for tests
        notebook1 = models.Notebook('Notebook 1', type1, '/test/notebook1.pdf')
        notebook2 = models.Notebook('Notebook 2', type2, '/test/notebook2.pdf')
        notebook2.total_pages = 10
        notebook2.first_page_number = 0
        notebook3 = models.Notebook('Notebook 3', type1, '/test/notebook3.pdf')
        notebook3.first_page_number = 2
        self.notebooks = [notebook1, notebook2, notebook3]
        for notebook in self.notebooks:
            self.db.save_notebook(notebook)

    def test_get_notebooks(self):
        self.assertListEqual(self.db.get_notebooks(), self.notebooks)

    def test_get_notebook_by_title(self):
        expected = self.notebooks[0]
        notebook = self.db.get_notebook_by_title(expected.title)
        self.assertEqual(notebook.title, expected.title)
        self.assertEqual(notebook.type, expected.type)
        self.assertEqual(str(notebook.path), expected.path)
        self.assertEqual(notebook.total_pages, expected.total_pages)
        self.assertEqual(
            notebook.first_page_number, expected.first_page_number)

    def test_get_notebook_by_path(self):
        expected = self.notebooks[0]
        notebook = self.db.get_notebook_by_path(expected.path)
        self.assertEqual(notebook.title, expected.title)
        self.assertEqual(notebook.type, expected.type)
        self.assertEqual(str(notebook.path), expected.path)
        self.assertEqual(notebook.total_pages, expected.total_pages)
        self.assertEqual(
            notebook.first_page_number, expected.first_page_number)

    def test_get_notebook_titles(self):
        titles = self.db.get_notebook_titles()
        expected = ['Notebook 1', 'Notebook 2', 'Notebook 3']
        self.assertListEqual(titles, expected)

    def test_get_types(self):
        self.assertListEqual(self.db.get_types(), self.types)

    def test_get_type_titles(self):
        titles = self.db.get_type_titles()
        expected = list(map(operator.attrgetter('title'), self.types))
        self.assertListEqual(titles, expected)

    def test_get_type_by_id(self):
        expected = self.types[0]
        type = self.db.get_type_by_id(1)
        self.assertEqual(type.title, expected.title)
        self.assertEqual(type.page_width, expected.page_width)
        self.assertEqual(type.page_height, expected.page_height)
        self.assertEqual(type.pages_paired, expected.pages_paired)

    def test_get_type_by_title(self):
        expected = self.types[0]
        type = self.db.get_type_by_title(expected.title)
        self.assertEqual(type.title, expected.title)
        self.assertEqual(type.page_width, expected.page_width)
        self.assertEqual(type.page_height, expected.page_height)
        self.assertEqual(type.pages_paired, expected.pages_paired)

    def test_notebook_exists(self):
        for notebook in self.notebooks:
            self.assertTrue(self.db.notebook_exists(notebook.title))

    def test_type_exists(self):
        for type in self.types:
            self.assertTrue(self.db.type_exists(type.title))

    def test_save_notebook(self):
        self.notebooks[0].id = 1
        self.notebooks[0].title = 'New Title'
        self.assertFalse(self.db.notebook_exists('New Title'))
        self.db.save_notebook(self.notebooks[0])
        self.assertTrue(self.db.notebook_exists('New Title'))

    def test_save_type(self):
        self.types[0].id = 1
        self.types[0].title = 'New Title'
        self.assertFalse(self.db.type_exists('New Title'))
        self.db.save_type(self.types[0])
        self.assertTrue(self.db.type_exists('New Title'))

    @mock.patch.object(sqlite3, 'connect', side_effect=sqlite3.Error)
    def test_errors(self, connect_mock):
        logging.disable()
        self.assertRaises(db.Error, db.DB)
        self.assertRaises(db.Error, self.db.get_notebooks)
        self.assertRaises(db.Error, self.db.get_notebook_by_title, '')
        self.assertRaises(db.Error, self.db.get_notebook_titles)
        self.assertRaises(db.Error, self.db.get_types)
        self.assertRaises(db.Error, self.db.get_type_titles)
        self.assertRaises(db.Error, self.db.get_type_by_id, 0)
        self.assertRaises(db.Error, self.db.get_type_by_title, '')
        self.assertRaises(db.Error, self.db.notebook_exists, '')
        self.assertRaises(db.Error, self.db.type_exists, '')
        self.assertRaises(db.Error, self.db.save_notebook, self.notebooks[0])
        self.assertRaises(db.Error, self.db.save_type, self.types[0])

    def tearDown(self):
        os.remove(self.DB_PATH)
