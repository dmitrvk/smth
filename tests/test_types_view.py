import unittest
from unittest import mock

from smth import views
from tests import testutils


class TestTypesView(unittest.TestCase):
    def test_show_types(self):
        view = views.TypesView()

        types = []

        for i in range(3):
            type = mock.MagicMock()
            type.title = f'Test{i}'
            type.page_width = i ** 2 * 100
            type.page_height = i ** 3 * 100
            types.append(type)

        output = testutils.capture_stdout(view.show_types, types)

        for i in range(3):
            self.assertIn(f'Test{i}', output)
            size = '{}x{}mm'.format(str(i ** 2 * 100), str(i ** 3 * 100))
            self.assertIn(size, output)

        # No types
        output = testutils.capture_stdout(view.show_types, [])
        self.assertIn('No types found', output)

