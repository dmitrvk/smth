import json
import pathlib

import pydrive.auth
import pydrive.drive


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

    def __init__(self):
        self._gdrive = pydrive.drive.GoogleDrive(self._auth())
        self._smth_folder_id = self._create_smth_folder_if_not_exists()

    def _auth(self) -> None:
        """Ask user to visit a link and paste a verification code."""
        gauth = pydrive.auth.GoogleAuth()
        gauth.settings['client_config_file'] = str(Cloud.SECRETS_PATH)

        if not Cloud.SECRETS_PATH.exists():
            with open(str(Cloud.SECRETS_PATH), 'w') as secrets_file:
                json.dump(Cloud.SECRETS, secrets_file)

        if Cloud.CREDENTIALS_PATH.exists():
            gauth.LoadCredentialsFile(str(Cloud.CREDENTIALS_PATH))
        else:
            gauth.CommandLineAuth()
            gauth.SaveCredentialsFile(str(Cloud.CREDENTIALS_PATH))

        return gauth

    def upload_file(self, path: pathlib.Path) -> None:
        """Upload file to 'smth' folder on Google Drive."""
        for file in self._get_list_of_pdf_files_in_smth_dir():
            if file['title'] == path.name:
                file.SetContentFile(str(path))
                file.Upload()
                return

        file_on_drive = self._gdrive.CreateFile({
            'title': path.name,
            'parents': [{"id": self._smth_folder_id}],
            'mimeType': 'application/pdf',
        })

        file_on_drive.SetContentFile(str(path))
        file_on_drive.Upload()

    def share_file(self, filename: str) -> None:
        """Share file in 'smth' folder on Google Drive and return a link."""
        for file in self._get_list_of_pdf_files_in_smth_dir():
            if file['title'] == filename:
                file.InsertPermission({
                    'type': 'anyone',
                    'value': 'anyone',
                    'role': 'reader',
                })

                return file['alternateLink']

    def _create_smth_folder_if_not_exists(self) -> str:
        """Return folder's id."""
        for folder in self._get_list_of_folders_in_root_dir():
            if folder['title'] == 'smth':
                return folder['id']

        folder_metadata = {
            'title': 'smth',
            'mimeType': 'application/vnd.google-apps.folder',
        }

        folder = self._gdrive.CreateFile(folder_metadata)
        folder.Upload()

        return folder['id']

    def _get_list_of_folders_in_root_dir(self):
        query = ("""'root' in parents and
                trashed=false and
                mimeType='application/vnd.google-apps.folder'""")

        return self._gdrive.ListFile({'q': query}).GetList()

    def _get_list_of_pdf_files_in_smth_dir(self):
        query = (f"""'{self._smth_folder_id}' in parents and
                trashed=false and
                mimeType='application/pdf'""")

        return self._gdrive.ListFile({'q': query}).GetList()
