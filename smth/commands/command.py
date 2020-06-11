import abc
from typing import List


class Command(abc.ABC):  # pylint: disable=too-few-public-methods
    """A command which can be executed with arguments."""

    @abc.abstractmethod
    def execute(self, args: List[str] = None):
        """Run command with the given arguments."""
