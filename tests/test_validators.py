import os
import unittest
from unittest import mock

from inquirer import errors
from pyfakefs import fake_filesystem_unittest as fakefs_unittest

from smth import validators


class TestNotebookValidator(unittest.TestCase):
    """Test user input validation when creating a notebook."""

    def setUp(self):
        self.db = mock.MagicMock()
        self.validator = validators.NotebookValidator(self.db)

    @fakefs_unittest.patchfs
    def test_validate_title(self, fs):
        self.db.notebook_exists.return_value = False

        self.assertTrue(self.validator.validate_title(None, 'Test'))

        # Empty title
        self.assertRaises(
            errors.ValidationError, self.validator.validate_title, None, '')
        self.assertRaises(
            errors.ValidationError, self.validator.validate_title, None, '   ')

        self.assertTrue(self.validator.validate_title(None, 'Test'))

        # Notebook already exists
        with mock.patch.object(self.db, 'notebook_exists', return_value=True):
            self.assertRaises(
                errors.ValidationError,
                self.validator.validate_title, None, 'Test')

        # Directory already exists
        fs.create_dir(os.path.expanduser('~/.local/share/smth/pages/Test'))
        with self.assertRaises(errors.ValidationError):
            self.validator.validate_title(None, 'Test')

    def test_validate_type(self):
        self.db.notebook_type_exists.return_value = True

        self.assertTrue(self.validator.validate_type(None, 'Test'))

        # Empty type
        self.assertRaises(
            errors.ValidationError, self.validator.validate_type, None, '')
        self.assertRaises(
            errors.ValidationError, self.validator.validate_type, None, '   ')

        # Type does not exist
        self.db.type_exists.return_value = False
        self.assertRaises(
            errors.ValidationError, self.validator.validate_type, None, 'Test')

    @fakefs_unittest.patchfs
    def test_validate_path(self, fs):
        self.assertTrue(
            self.validator.validate_path(None, '/home/test/file.pdf'))
        self.assertTrue(
            self.validator.validate_path(None, '~/file.pdf'))
        self.assertTrue(
            self.validator.validate_path(None, '$HOME/file.pdf'))

        # Empty path
        self.assertRaises(
            errors.ValidationError, self.validator.validate_path, None, '')
        self.assertRaises(
            errors.ValidationError, self.validator.validate_path, None, '   ')

        # File already exists
        fs.create_file('test')
        self.assertRaises(
            errors.ValidationError, self.validator.validate_path, None, 'test')

    def test_validate_first_page_number(self):
        self.assertTrue(self.validator.validate_first_page_number(None, '0'))
        self.assertTrue(self.validator.validate_first_page_number(None, '1'))

        # Number < 0
        self.assertRaises(
            errors.ValidationError,
            self.validator.validate_first_page_number, None, '-5')

        # Not a number
        self.assertRaises(
            errors.ValidationError,
            self.validator.validate_first_page_number, None, 'test')


class TestScanPreferencesValidator(unittest.TestCase):
    """Test user input validation when choosing scan preferences."""
    def setUp(self):
        self.validator = validators.ScanPreferencesValidator()

    def test_validate_number_of_pages_to_append(self):
        self.assertTrue(
            self.validator.validate_number_of_pages_to_append(None, '1'))
        self.assertTrue(
            self.validator.validate_number_of_pages_to_append(None, ''))
        self.assertTrue(
            self.validator.validate_number_of_pages_to_append(None, '   '))

        # Number < 0
        self.assertRaises(
            errors.ValidationError,
            self.validator.validate_number_of_pages_to_append, None, '-1')

        # Not a number
        self.assertRaises(
            errors.ValidationError,
            self.validator.validate_number_of_pages_to_append, None, 'test')
