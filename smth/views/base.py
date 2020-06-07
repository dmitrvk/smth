import sys


class BaseView:
    """"User interface base class."""

    def show_info(self, message: str) -> None:
        """Print message to stdout."""
        print(message)

    def show_error(self, message: str) -> None:
        """Print message to stderr."""
        print(message, file=sys.stderr)
