import os
import unittest
from unittest import mock

from pyfakefs import fake_filesystem_unittest as fakefs_unittest
from PyInquirer import ValidationError

from smth import validators


class TestNotebookValidator(unittest.TestCase):
    """Test user input validation when creating a notebook."""

    def setUp(self):
        self.db = mock.MagicMock()
        self.validator = validators.NotebookValidator(self.db)

    @fakefs_unittest.patchfs
    def test_validate_title(self, fs):
        self.db.notebook_exists.return_value = False

        self.assertTrue(self.validator.validate_title('Test'))

        # Empty title
        self.assertRaises(
            ValidationError, self.validator.validate_title, '')
        self.assertRaises(
            ValidationError, self.validator.validate_title, '   ')

        self.assertTrue(self.validator.validate_title('Test'))

        # Notebook already exists
        with mock.patch.object(self.db, 'notebook_exists', return_value=True):
            self.assertRaises(
                ValidationError,
                self.validator.validate_title, 'Test')

        # Directory already exists
        fs.create_dir(os.path.expanduser('~/.local/share/smth/pages/Test'))
        with self.assertRaises(ValidationError):
            self.validator.validate_title('Test')

    def test_validate_type(self):
        self.db.notebook_type_exists.return_value = True

        self.assertTrue(self.validator.validate_type('Test'))

        # Empty type
        self.assertRaises(
            ValidationError, self.validator.validate_type, '')
        self.assertRaises(
            ValidationError, self.validator.validate_type, '   ')

        # Type does not exist
        self.db.type_exists.return_value = False
        self.assertRaises(
            ValidationError, self.validator.validate_type, 'Test')

    @fakefs_unittest.patchfs
    def test_validate_path(self, fs):
        self.assertTrue(
            self.validator.validate_path('/home/test/file.pdf'))
        self.assertTrue(
            self.validator.validate_path('~/file.pdf'))
        self.assertTrue(
            self.validator.validate_path('$HOME/file.pdf'))

        # Empty path
        self.assertRaises(
            ValidationError, self.validator.validate_path, '')
        self.assertRaises(
            ValidationError, self.validator.validate_path, '   ')

        # File already exists
        fs.create_file('test')
        self.assertRaises(
            ValidationError, self.validator.validate_path, 'test')

    def test_validate_first_page_number(self):
        self.assertTrue(self.validator.validate_first_page_number('0'))
        self.assertTrue(self.validator.validate_first_page_number('1'))

        # Number < 0
        self.assertRaises(
            ValidationError,
            self.validator.validate_first_page_number, '-5')

        # Number > 100
        self.assertRaises(
            ValidationError,
            self.validator.validate_first_page_number, '5000')
        self.assertRaises(
            ValidationError,
            self.validator.validate_first_page_number, '500')

        # Not a number
        self.assertRaises(
            ValidationError,
            self.validator.validate_first_page_number, 'test')


class TestScanPreferencesValidator(unittest.TestCase):
    """Test user input validation when choosing scan preferences."""
    def setUp(self):
        self.validator = validators.ScanPreferencesValidator()

    def test_validate_number_of_pages_to_append(self):
        self.assertTrue(
            self.validator.validate_number_of_pages_to_append('1'))
        self.assertTrue(
            self.validator.validate_number_of_pages_to_append(''))
        self.assertTrue(
            self.validator.validate_number_of_pages_to_append('   '))

        # Number < 0
        self.assertRaises(
            ValidationError,
            self.validator.validate_number_of_pages_to_append, '-1')

        # Number > 100
        self.assertRaises(
            ValidationError,
            self.validator.validate_number_of_pages_to_append, '5000')
        self.assertRaises(
            ValidationError,
            self.validator.validate_number_of_pages_to_append, '500')

        # Not a number
        self.assertRaises(
            ValidationError,
            self.validator.validate_number_of_pages_to_append, 'test')
