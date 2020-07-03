import json
import logging
import pathlib
from typing import List

from smth import db

from . import command

log = logging.getLogger(__name__)


class UploadCommand(command.Command):  # pylint: disable=too-few-public-methods  # noqa: E501
    """A command for uploading notebooks to Google Drive."""

    CLIENT_SECRETS = {
        "installed": {
            "client_id": "393847868490-0nbggpkeq4vn47050f2b10blmghp1uo7.apps.googleusercontent.com",  # noqa: E501
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_secret": "UgLqgONjhpvbMEuhUbIdVzub",
            "redirect_uris": [
                "urn:ietf:wg:oauth:2.0:oob",
                "http://localhost",
            ],
        },
    }

    CLIENT_SECRETS_PATH = pathlib.Path(
        '~/.config/smth/client_secrets.json').expanduser()

    CREDENTIALS_PATH = pathlib.Path(
        '~/.config/smth/credentials.json').expanduser()

    def execute(self, args: List[str] = None):
        """Upload notebook's PDF file to Google Drive."""
        try:
            import pydrive.auth
            import pydrive.drive
        except ImportError:
            self._exit_with_error('PyDrive not found.')

        gauth = pydrive.auth.GoogleAuth()
        gauth.settings['client_config_file'] = str(self.CLIENT_SECRETS_PATH)

        if not self.CLIENT_SECRETS_PATH.exists():
            with open(str(self.CLIENT_SECRETS_PATH), 'w') as secrets_file:
                json.dump(self.CLIENT_SECRETS, secrets_file)

        if self.CREDENTIALS_PATH.exists():
            gauth.LoadCredentialsFile(str(self.CREDENTIALS_PATH))
        else:
            gauth.CommandLineAuth()
            gauth.SaveCredentialsFile(str(self.CREDENTIALS_PATH))

        drive = pydrive.drive.GoogleDrive(gauth)

        try:
            notebooks = self._db.get_notebook_titles()
        except db.Error as exception:
            self._exit_with_error(exception)

        if notebooks:
            notebook = self.view.ask_for_notebook(notebooks)

            self.view.show_separator()

            if notebook:
                path = self._db.get_notebook_by_title(notebook).path

                smth_folder_id = self._create_smth_folder_if_not_exists(drive)

                self.view.show_separator()

                self.view.show_info('Checking if file already exists...')

                query = (f"""'{smth_folder_id}' in parents and
                        trashed=false and
                        mimeType='application/pdf'""")
                file_list = drive.ListFile({'q': query}).GetList()

                for file in file_list:
                    if file['title'] == path.name:
                        override_file = self.view.confirm(
                            f"File 'smth/{path.name}' "
                            "exists on Google Drive. Override?")

                        if override_file:
                            self.view.show_info(
                                f"Uploading '{str(path)}' to Google Drive...")
                            file.SetContentFile(str(path))
                            file.Upload()
                            self.view.show_info(
                                f"File '{path.name}' "
                                "uploaded to Google Drive.")

                        return

                file_on_drive = drive.CreateFile({
                    'title': path.name,
                    'parents': [{"id": smth_folder_id}],
                    'mimeType': 'application/pdf',
                })

                file_on_drive.SetContentFile(str(path))
                file_on_drive.Upload()

                self.view.show_info(
                    f"File '{path.name}' uploaded to Google Drive.")
        else:
            self.view.show_info('No notebooks found.')

    def _create_smth_folder_if_not_exists(self, drive) -> str:
        self.view.show_info("Checking if folder 'smth' exists...")

        query = ("""'root' in parents and
                trashed=false and
                mimeType='application/vnd.google-apps.folder'""")
        file_list = drive.ListFile({'q': query}).GetList()

        for folder in file_list:
            if folder['title'] == 'smth':
                self.view.show_info('OK. Folder exists.')
                return folder['id']

        folder_metadata = {
            'title': 'smth',
            'mimeType': 'application/vnd.google-apps.folder',
        }

        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        self._smth_folder_id = folder['id']

        self.view.show_info("Created folder 'smth'.")

        return folder['id']
