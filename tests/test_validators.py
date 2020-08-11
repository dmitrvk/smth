import os
import unittest
from unittest import mock

from pyfakefs import fake_filesystem_unittest as fakefs_unittest
from PyInquirer import ValidationError

from smth import validators


class NotebookValidatorTestCase(unittest.TestCase):
    """Test user input validation when creating a notebook."""

    def setUp(self):
        self.db = mock.MagicMock()
        self.db.get_notebook_by_path.return_value = mock.MagicMock(**{
            'title': 'Untitled',
        })

        self.validator = validators.NotebookValidator(self.db)

    @fakefs_unittest.patchfs
    def test_validate_title(self, fs):
        self.db.notebook_exists.return_value = False

        self.assertTrue(self.validator.validate_title('Test'))

        # Empty title
        self.assertRaises(ValidationError, self.validator.validate_title, '')
        self.assertRaises(ValidationError, self.validator.validate_title, '  ')

        # Title contains '/' symbol
        self.assertRaises(ValidationError, self.validator.validate_title, 'a/')

        # Notebook already exists
        with mock.patch.object(self.db, 'notebook_exists', return_value=True):
            self.assertRaises(
                ValidationError,
                self.validator.validate_title, 'Test')

        # Directory with pages already exists
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
            self.validator.validate_path('/home/test/notebook.pdf'))
        self.assertTrue(
            self.validator.validate_path('~/notebook.pdf'))
        self.assertTrue(
            self.validator.validate_path('$HOME/notebook.pdf'))

        # Empty path
        self.assertRaises(
            ValidationError, self.validator.validate_path, '')
        self.assertRaises(
            ValidationError, self.validator.validate_path, '   ')

        # File already exists
        fs.create_file('test')
        self.assertRaises(
            ValidationError, self.validator.validate_path, 'test')

    @fakefs_unittest.patchfs
    def test_validate_path_already_taken(self, fs):
        del fs  # Unused, but need to patch filesystem

        notebook = mock.MagicMock(**{
            'title': 'notebook',
        })

        db = mock.MagicMock(**{
            'get_notebook_by_path.return_value': notebook,
        })

        validator = validators.NotebookValidator(db)

        self.assertRaises(
            ValidationError, validator.validate_path, '/test/path.pdf')

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


class NotebookUpdateValidatorTestCase(unittest.TestCase):
    """Test user input validation when updating a notebook."""

    def setUp(self):
        self.validator = validators.NotebookUpdateValidator()

    def test_validate_title(self):
        self.assertTrue(self.validator.validate_title('Test'))
        self.assertRaises(
            ValidationError, self.validator.validate_title, '')
        self.assertRaises(
            ValidationError, self.validator.validate_title, '   ')

    def test_validate_path(self):
        self.assertTrue(
            self.validator.validate_path('/home/test/notebook.pdf'))
        self.assertTrue(
            self.validator.validate_path('~/notebook.pdf'))
        self.assertTrue(
            self.validator.validate_path('$HOME/notebook.pdf'))
        self.assertRaises(
            ValidationError, self.validator.validate_path, '')
        self.assertRaises(
            ValidationError, self.validator.validate_path, '   ')


class TypeValidatorTestCase(unittest.TestCase):
    def setUp(self):
        self.db = mock.MagicMock(**{
            'type_exists.return_value': False,
        })

        self.validator = validators.TypeValidator(self.db)

    def test_validate_title(self):
        self.assertTrue(self.validator.validate_title('Test Type'))

        # Empty
        self.assertRaises(
            ValidationError, self.validator.validate_title, '')

        # Exists
        self.db.type_exists.return_value = True
        self.assertRaises(
            ValidationError, self.validator.validate_title, 'Title')

    def test_validate_page_size(self):
        self.assertTrue(self.validator.validate_page_size('10'))
        self.assertTrue(self.validator.validate_page_size('100'))
        self.assertTrue(self.validator.validate_page_size('1000'))

        # Not a number
        self.assertRaises(
            ValidationError, self.validator.validate_page_size, 'size10')

        # Too small
        self.assertRaises(
            ValidationError, self.validator.validate_page_size, '1')

        # Too large
        self.assertRaises(
            ValidationError, self.validator.validate_page_size, '10000')


class PagesToScanValidatorTestCase(unittest.TestCase):
    """Test user input validation when choosing scan preferences."""
    def setUp(self):
        self.notebook = mock.MagicMock(**{
            'first_page_number': 1,
            'total_pages': 10,
        })
        self.validator = validators.PagesToScanValidator(self.notebook)

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

    def test_validate_pages_to_replace(self):
        self.assertTrue(
            self.validator.validate_pages_to_replace('1 2 3-5 4-7')
        )

        # Negative number
        self.assertRaises(
            ValidationError, self.validator.validate_pages_to_replace, '-1 2')

        # Not a number
        self.assertRaises(
            ValidationError, self.validator.validate_pages_to_replace, ' a 2')

        # Number < first page number
        self.assertRaises(
            ValidationError, self.validator.validate_pages_to_replace, '0')

        # Number > max page number
        self.assertRaises(
            ValidationError, self.validator.validate_pages_to_replace, '20')

        # Invalid range
        self.assertRaises(
            ValidationError, self.validator.validate_pages_to_replace, '-1-2')
        self.assertRaises(
            ValidationError, self.validator.validate_pages_to_replace, '5-2')

        # Invalid range start
        self.assertRaises(
            ValidationError, self.validator.validate_pages_to_replace, '0-3')

        # Invalid range end
        self.assertRaises(
            ValidationError, self.validator.validate_pages_to_replace, '2-30')
