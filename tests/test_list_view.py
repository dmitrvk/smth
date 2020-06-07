import unittest
from unittest import mock

from smth import views
from tests import testutils


class TestListView(unittest.TestCase):
    def test_show_notebooks(self):
        view = views.ListView()

        notebooks = []

        for i in range(3):
            notebook = mock.MagicMock()
            notebook.title = f'Test{i}'
            notebook.total_pages = i ** 2
            notebook.type = mock.MagicMock()
            notebook.type.title = 'Test Type'
            notebooks.append(notebook)

        output = testutils.capture_stdout(view.show_notebooks, notebooks)

        for i in range(3):
            self.assertIn(f'Test{i}', output)
            self.assertIn(str(i ** 2), output)
            self.assertIn('Test Type', output)

        # No notebooks
        output = testutils.capture_stdout(view.show_notebooks, [])
        self.assertIn('No notebooks found', output)
