import argparse
import unittest
from unittest import mock

from smth import commands


class CommandTestCase(unittest.TestCase):
    def test_cannot_instantiate(self):
        self.assertRaises(TypeError, commands.Command)

        class ConcreteCommand(commands.Command):
            pass

        self.assertRaises(TypeError, ConcreteCommand)

    def test_execute(self):
        class ConcreteCommand(commands.Command):
            def execute(self, args: argparse.Namespace):
                super().execute(args)

        args = mock.MagicMock()
        ConcreteCommand(None, None).execute(args)
