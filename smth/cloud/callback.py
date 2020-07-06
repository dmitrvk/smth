import abc
import pathlib


class Callback(abc.ABC):
    """Used to notify about cloud's events. Must be subclassed."""

    @abc.abstractmethod
    def on_start_uploading_file(self, path: pathlib.Path) -> None:
        pass

    @abc.abstractmethod
    def on_confirm_override_file(self, filename: str) -> bool:
        """Return True if allowed to override the file."""
        pass

    @abc.abstractmethod
    def on_finish_uploading_file(self, path: pathlib.Path) -> None:
        pass

    @abc.abstractmethod
    def on_start_sharing_file(self, filename: str) -> None:
        pass

    @abc.abstractmethod
    def on_finish_sharing_file(self, filename: str, link: str) -> None:
        pass

    @abc.abstractmethod
    def on_create_smth_folder(self) -> None:
        pass

    @abc.abstractmethod
    def on_error(self, message: str) -> None:
        pass
