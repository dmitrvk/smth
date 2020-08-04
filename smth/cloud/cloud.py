# License: GNU GPL Version 3

"""The module provides the Cloud class for uploading and sharing files.

    Typical usage example:

    cloud_ = cloud.Cloud(callback)
    cloud_.upload_file(path)
"""

import json
import pathlib

from . import callback

try:
    import httplib2
    import pydrive.auth
    import pydrive.drive
    import pydrive.files
    import oauth2client.file
except ImportError:
    pass


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

    def __init__(self, callback_: callback.Callback):
        self._callback = callback_
        self._gdrive = pydrive.drive.GoogleDrive(self._auth())
        self._smth_folder_id = self._create_smth_folder_if_not_exists()

    def _auth(self) -> None:
        """Ask user to visit a link and paste a verification code."""
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
        """Upload file to 'smth' folder on Google Drive."""
        self._callback.on_start_uploading_file(path)

        for file_on_drive in self._get_list_of_pdf_files_in_smth_dir():
            if file_on_drive['title'] == path.name:
                if self._callback.on_confirm_override_file(path.name):
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
        """Share file in 'smth' folder on Google Drive and return a link."""
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
