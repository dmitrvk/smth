# License: GNU GPL Version 3

"""The module provides the Cloud class with callbacks.

It is used to upload and share files on Google Drive.

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
import json
import pathlib

try:
    import httplib2
    import pydrive.auth
    import pydrive.drive
    import pydrive.files
    import oauth2client.file
except ImportError:
    pass


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
    def on_confirm_overwrite_file(self, filename: str) -> bool:
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


class Cloud:
    """Represents a Google Drive cloud storage."""

    SECRETS = {
        "installed": {
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "client_id": ("393847868490-0nbggpkeq4vn47050f2b10blmghp1uo7."
                          "apps.googleusercontent.com"),
            "client_secret": "UgLqgONjhpvbMEuhUbIdVzub",
            "redirect_uris": [
                "urn:ietf:wg:oauth:2.0:oob",
                "http://localhost",
            ],
            "token_uri": "https://oauth2.googleapis.com/token",
        },
    }

    SECRETS_PATH = pathlib.Path(
        '~/.config/smth/client_secrets.json').expanduser()

    CREDENTIALS_PATH = pathlib.Path(
        '~/.config/smth/credentials.json').expanduser()

    def __init__(self, callback_: Callback):
        self._callback = callback_
        self._gdrive = pydrive.drive.GoogleDrive(self._auth())
        self._smth_folder_id = self._create_smth_folder_if_not_exists()

    def _auth(self):
        """Performs the authentication and authorization.

        Asks user to visit a link and paste a verification code.

        Two files are involved in the authentication and authorization
        processes:
            ~/.config/smth/client_secrets.json
            ~/.config/smth/credentials.json
        The first file contains the information about this command-line
        application as a client to the Google Cloud application.  The second
        file contains credentials for accessing the user's Google Drive.

        Returns:
            GoogleAuth object after successful auth.
        """
        gauth = pydrive.auth.GoogleAuth()
        gauth.settings['client_config_file'] = str(Cloud.SECRETS_PATH)

        self._prepare_secrets_file()

        if Cloud.CREDENTIALS_PATH.exists():
            storage = oauth2client.file.Storage(str(Cloud.CREDENTIALS_PATH))
            credentials = storage.get()

            if not credentials:
                message = ("Invalid credentials file "
                           f"'{str(Cloud.CREDENTIALS_PATH)}'.\n"
                           "Check if the file is readable. "
                           "You may want to delete it to perform auth again.")
                self._callback.on_error(message)

            try:
                gauth.LoadCredentialsFile(str(Cloud.CREDENTIALS_PATH))
            except (OSError,
                    pydrive.auth.InvalidCredentialsError) as exception:
                self._callback.on_error(str(exception))
        else:
            try:
                with open(str(Cloud.CREDENTIALS_PATH), 'a') as creds_file:
                    creds_file.write('')  # Check if writable

                gauth.CommandLineAuth()
                gauth.SaveCredentialsFile(str(Cloud.CREDENTIALS_PATH))
            except (OSError,
                    httplib2.ServerNotFoundError,
                    pydrive.auth.InvalidCredentialsError) as exception:
                self._callback.on_error(str(exception))
            except KeyboardInterrupt:
                self._callback.on_error('Keyboard interrupt during auth.')

        return gauth

    def _prepare_secrets_file(self) -> None:
        def read_secrets():
            try:
                with open(str(Cloud.SECRETS_PATH), 'r') as secrets_file:
                    return json.loads(secrets_file.read())
            except json.JSONDecodeError:
                return {}
            except OSError as exception:
                self._callback.on_error(str(exception))

        def write_secrets():
            try:
                with open(str(Cloud.SECRETS_PATH), 'w') as sec_file:
                    json.dump(Cloud.SECRETS, sec_file)
            except OSError as exception:
                self._callback.on_error(str(exception))

        if Cloud.SECRETS_PATH.exists():
            if read_secrets() != Cloud.SECRETS:
                write_secrets()
        else:
            write_secrets()

    def upload_file(self, path: pathlib.Path) -> None:
        """Uploads file to 'smth' folder on Google Drive.

        Args:
            path:
                Path to file which should be uploaded.
        """
        self._callback.on_start_uploading_file(path)

        for file_on_drive in self._get_list_of_pdf_files_in_smth_dir():
            if file_on_drive['title'] == path.name:
                if self._callback.on_confirm_overwrite_file(path.name):
                    self._upload(path, file_on_drive)

                return

        file_on_drive = self._gdrive.CreateFile({
            'title': path.name,
            'parents': [{"id": self._smth_folder_id}],
            'mimeType': 'application/pdf',
        })

        self._upload(path, file_on_drive)

    def _upload(self, path: pathlib.Path, file_on_drive):
        try:
            file_on_drive.SetContentFile(str(path))
            file_on_drive.Upload()
            self._callback.on_finish_uploading_file(path)
        except (OSError,
                httplib2.ServerNotFoundError,
                pydrive.files.ApiRequestError) as exception:
            self._callback.on_error(str(exception))
        except KeyboardInterrupt:
            message = 'Keyboard interrupt while uploading file.'
            self._callback.on_error(message)

    def share_file(self, filename: str) -> None:
        """Shares file in 'smth' folder on Google Drive and returns a link.

        Args:
            filename:
                Name of file which should be shared.
        """
        self._callback.on_start_sharing_file(filename)

        for file in self._get_list_of_pdf_files_in_smth_dir():
            if file['title'] == filename:
                try:
                    file.InsertPermission({
                        'type': 'anyone',
                        'value': 'anyone',
                        'role': 'reader',
                    })

                    self._callback.on_finish_sharing_file(
                        filename, file['alternateLink'])

                    return
                except (httplib2.ServerNotFoundError,
                        pydrive.files.ApiRequestError) as exception:
                    self._callback.on_error(str(exception))
                except KeyboardInterrupt:
                    message = 'Keyboard interrupt while sharing file.'
                    self._callback.on_error(message)

        message = f"File '{filename}' not found on Google Drive."
        self._callback.on_error(message)

    def _create_smth_folder_if_not_exists(self) -> str:
        """Return folder's id."""
        for folder in self._get_list_of_folders_in_root_dir():
            if folder['title'] == 'smth':
                return folder['id']

        folder_metadata = {
            'title': 'smth',
            'mimeType': 'application/vnd.google-apps.folder',
        }

        try:
            folder = self._gdrive.CreateFile(folder_metadata)
            folder.Upload()
            self._callback.on_create_smth_folder()
        except httplib2.ServerNotFoundError as exception:
            self._callback.on_error(str(exception))
        except KeyboardInterrupt:
            message = ("Keyboard interrupt while creating 'smth' folder "
                       "on Google Drive.")
            self._callback.on_error(message)

        return folder['id']

    def _get_list_of_folders_in_root_dir(self):
        query = ("""'root' in parents and
                trashed=false and
                mimeType='application/vnd.google-apps.folder'""")

        try:
            return self._gdrive.ListFile({'q': query}).GetList()
        except httplib2.ServerNotFoundError as exception:
            self._callback.on_error(str(exception))
            return []
        except KeyboardInterrupt:
            message = ('Keyboard interrupt while loading the list of '
                       'files in root folder on Google Drive.')
            self._callback.on_error(message)
            return []

    def _get_list_of_pdf_files_in_smth_dir(self):
        query = (f"""'{self._smth_folder_id}' in parents and
                trashed=false and
                mimeType='application/pdf'""")

        try:
            return self._gdrive.ListFile({'q': query}).GetList()
        except httplib2.ServerNotFoundError as exception:
            self._callback.on_error(str(exception))
            return []
        except KeyboardInterrupt:
            message = ("Keyboard interrupt while loading the list of "
                       "files in 'smth' folder on Google Drive.")
            self._callback.on_error(message)
            return []
