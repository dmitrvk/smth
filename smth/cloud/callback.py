# License: GNU GPL Version 3

"""The module provides two callbacks to subscribe to the Cloud's events.

    Typical usage example:

    class CloudCallback(cloud.UploadingCallback):
        def __init__(...):
            super().__init__()
            ...

        def on_start_uploading_file(self, path):
            ...

        # Override all methods...

   cloud_ = cloud.Cloud(CloudCallback(...))
   cloud_.upload_file(path)
"""


import abc
import pathlib


class Callback(abc.ABC):  # pylint: disable=too-few-public-methods
    """Used to notify about cloud's events. Must be subclassed."""

    @abc.abstractmethod
    def on_create_smth_folder(self) -> None:
        """Called when 'smth' folder created on Google Drive."""

    @abc.abstractmethod
    def on_error(self, message: str) -> None:
        """Called when error occurs while working with cloud.

        Args:
            message:
                A string with error message.
        """


class UploadingCallback(Callback):
    """Used to notify about uploading events. Must be subclassed."""
    @abc.abstractmethod
    def on_start_uploading_file(self, path: pathlib.Path) -> None:
        """Called when file is about to be uploaded to Google Drive.

        Args:
            path:
                Path to file which is about to be uploaded.
        """

    @abc.abstractmethod
    def on_confirm_override_file(self, filename: str) -> bool:
        """Called when the user confirmation needed before uploading a file.

        The method should return True if the user allowed to overwrite the
        file.

        Args:
            filename:
                Name of file on Google Drive which will be overwritten.

        Returns:
            True, if the user confirmed the overwriting.  False otherwise.
        """

    @abc.abstractmethod
    def on_finish_uploading_file(self, path: pathlib.Path) -> None:
        """Called when file is uploaded to Google Drive.

        Args:
            path:
                Path to file which was uploaded to Google Drive.
        """


class SharingCallback(abc.ABC):
    """Used to notify about sharing events. Must be subclassed."""

    @abc.abstractmethod
    def on_start_sharing_file(self, filename: str) -> None:
        """Called when file is about to be shared.

        Args:
            filename:
                Name of file which will be shared.
        """

    @abc.abstractmethod
    def on_finish_sharing_file(self, filename: str, link: str) -> None:
        """Called when file is shared and link is provided.

        Args:
            filename:
                Name of shared file.
            link:
                File URL on the Google Drive.
        """
