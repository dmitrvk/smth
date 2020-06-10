import abc


class Command(abc.ABC):
    """A command which can be executed with arguments."""

    @abc.abstractmethod
    def execute(self, *args, **kwargs):
        pass
