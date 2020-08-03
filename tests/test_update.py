import logging
import pathlib
from unittest import mock

from pyfakefs import fake_filesystem_unittest

from smth import commands, models


class UpdateCommandTestCase(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        logging.disable()

        type_ = models.NotebookType('A4', 210, 297)
        path = pathlib.Path('/test/notebook.pdf')
        self.notebook = models.Notebook('notebook', type_, path)

        self.fs.create_file(str(self.notebook.path))

        self.pages_dir = pathlib.Path('~/.local/share/smth/pages').expanduser()
        self.fs.create_dir(str(self.pages_dir / self.notebook.title))

        untitled_notebook = models.Notebook('Untitled', None, None)

        self.db = mock.MagicMock(**{
            'get_notebook_titles.return_value': [self.notebook.title],
            'get_notebook_by_title.return_value': self.notebook,
            'get_notebook_by_path.return_value': untitled_notebook,
            'notebook_exists.return_value': False,
        })

        self.view = mock.MagicMock(**{
            'ask_for_notebook.return_value': self.notebook.title,
        })

    def test_execute(self):
        old_title = self.notebook.title

        old_path = self.notebook.path
        new_path = pathlib.Path('/test/path')

        answers = {
            'title': 'new',
            'path': str(new_path),
        }

        self.view.ask_for_updated_notebook_properties.return_value = answers

        commands.UpdateCommand(self.db, self.view).execute()

        self.db.save_notebook.assert_called_once()

        self.assertFalse(old_path.exists())
        self.assertTrue((new_path / 'new.pdf').exists())

        self.assertFalse((self.pages_dir / old_title).exists())
        self.assertTrue((self.pages_dir / answers['title']).exists())

    def test_execute_new_path_already_exists(self):
        new_path = pathlib.Path('/test/path/notebook.pdf')
        self.fs.create_file(str(new_path))

        answers = {
            'title': 'notebook',
            'path': str(new_path),
        }

        self.view.ask_for_updated_notebook_properties.return_value = answers

        with self.assertRaises(SystemExit):
            commands.UpdateCommand(self.db, self.view).execute()

        self.db.save_notebook.assert_not_called()

    def test_execute_no_notebook_chosen(self):
        self.view.ask_for_notebook.return_value = None
        commands.UpdateCommand(self.db, self.view).execute()
        self.db.save_notebook.assert_not_called()

    def test_execute_no_new_notebook_properties(self):
        self.view.ask_for_updated_notebook_properties.return_value = None
        commands.UpdateCommand(self.db, self.view).execute()
        self.db.save_notebook.assert_not_called()

    def test_execute_notebook_with_title_already_exists(self):
        self.db.notebook_exists.return_value = True

        answers = {
            'title': 'new',
            'path': str(self.notebook.path),
        }

        self.view.ask_for_updated_notebook_properties.return_value = answers

        with self.assertRaises(SystemExit):
            commands.UpdateCommand(self.db, self.view).execute()

        self.db.save_notebook.assert_not_called()

    def test_execute_path_already_taken_by_another_notebook(self):
        path = pathlib.Path('/new/path.pdf')

        existing_notebook = models.Notebook('another', None, path)
        self.db.get_notebook_by_path.return_value = existing_notebook

        answers = {
            'title': 'notebook',
            'path': str(path),
        }

        self.view.ask_for_updated_notebook_properties.return_value = answers

        with self.assertRaises(SystemExit):
            commands.UpdateCommand(self.db, self.view).execute()

        self.db.save_notebook.assert_not_called()

    def test_execute_no_notebook(self):
        self.db.get_notebook_titles.return_value = []

        commands.UpdateCommand(self.db, self.view).execute()

        self.view.ask_for_notebook.assert_not_called()
        self.db.save_notebook.assert_not_called()
