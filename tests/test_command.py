import unittest
from typing import List

from smth import commands


class CommandTestCase(unittest.TestCase):
    def test_cannot_instantiate(self):
        self.assertRaises(TypeError, commands.Command)

        class ConcreteCommand(commands.Command):
            pass

        self.assertRaises(TypeError, ConcreteCommand)

    def test_execute(self):
        class ConcreteCommand(commands.Command):
            def execute(self, args: List[str] = None):
                super().execute()

        ConcreteCommand(None, None).execute()
