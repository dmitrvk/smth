import json
import logging
import pathlib
from typing import List

from smth import commands, db

log = logging.getLogger(__name__)


class UploadCommand(commands.Command):  # pylint: disable=too-few-public-methods  # noqa: E501
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
        self._auth()

        try:
            notebooks = self._db.get_notebook_titles()
        except db.Error as exception:
            self._exit_with_error(exception)

        if notebooks:
            notebook = self.view.ask_for_notebook(notebooks)

            if notebook:
                path = self._db.get_notebook_by_title(notebook).path
                self.view.show_info(f"File '{path}' should be uploaded to Google Drive here.")  # noqa: E501
                self.view.show_info('This feature will be implemented in future versions')  # noqa: E501
        else:
            self.view.show_info('No notebooks found.')

    def _auth(self):
        try:
            import pydrive.auth
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
