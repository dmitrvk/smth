import logging
import pathlib
from unittest import mock

from pyfakefs import fake_filesystem_unittest

from smth import commands, db, models


class DeleteCommandTestCase(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        logging.disable()

        self.notebook = models.Notebook(
            'notebook', None, pathlib.Path('/test/path.pdf'))

        self.db = mock.MagicMock(**{
            'get_notebook_titles.return_value': [self.notebook.title],
            'get_notebook_by_title.return_value': self.notebook,
        })

        self.view = mock.MagicMock(**{
            'ask_for_notebook.return_value': self.notebook.title,
            'confirm.return_value': True,
        })

        self.fs.create_file(self.notebook.path)

        pages_root = pathlib.Path('~/.local/share/smth/pages').expanduser()
        self.pages_dir_path = pages_root / self.notebook.title
        self.fs.create_dir(self.pages_dir_path)

    def test_execute(self):
        commands.DeleteCommand(self.db, self.view).execute()

        self.db.delete_notebook_by_id.assert_called_once()
        self.assertTrue(self.notebook.path.exists())
        self.assertFalse(self.pages_dir_path.exists())

    def test_execute_no_notebook_chosen(self):
        self.view.ask_for_notebook.return_value = ''
        commands.DeleteCommand(self.db, self.view).execute()

        self.db.delete_notebook_by_id.assert_not_called()
        self.assertTrue(self.notebook.path.exists())
        self.assertTrue(self.pages_dir_path.exists())

    def test_execute_no_confirmation(self):
        self.view.confirm.return_value = False
        commands.DeleteCommand(self.db, self.view).execute()

        self.db.delete_notebook_by_id.assert_not_called()
        self.assertTrue(self.notebook.path.exists())
        self.assertTrue(self.pages_dir_path.exists())

    def test_execute_db_error(self):
        self.db.get_notebook_titles.side_effect = db.Error()

        command = commands.DeleteCommand(self.db, self.view)

        self.assertRaises(SystemExit, command.execute)
        self.db.delete_notebook_by_id.assert_not_called()
        self.assertTrue(self.notebook.path.exists())
        self.assertTrue(self.pages_dir_path.exists())
        self.view.show_error.assert_called()
