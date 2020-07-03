import json
import logging
from typing import List

from smth import db

from . import command, upload

log = logging.getLogger(__name__)


class ShareCommand(command.Command):  # pylint: disable=too-few-public-methods
    """A command for sharing notebooks."""

    def execute(self, args: List[str] = None):
        """Share notebook and show a link."""
        try:
            import pydrive.auth
            import pydrive.drive
        except ImportError:
            self._exit_with_error('PyDrive not found.')

        self.CLIENT_SECRETS_PATH = upload.UploadCommand.CLIENT_SECRETS_PATH
        self.CREDENTIALS_PATH = upload.UploadCommand.CREDENTIALS_PATH

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

            if not notebook:
                return

            path = self._db.get_notebook_by_title(notebook).path

            self.view.show_info("Looking for folder 'smth'...")

            query = ("""'root' in parents and
                    trashed=false and
                    mimeType='application/vnd.google-apps.folder'""")
            file_list = drive.ListFile({'q': query}).GetList()

            smth_folder_id = ''
            for folder in file_list:
                if folder['title'] == 'smth':
                    self.view.show_info('OK. Folder exists.')
                    smth_folder_id = folder['id']

            if not smth_folder_id:
                self.view.show_info(
                    "Folder 'smth' not found on Google Drive.")
                return

            self.view.show_separator()

            self.view.show_info('Looking for a file...')

            query = (f"""'{smth_folder_id}' in parents and
                    trashed=false and
                    mimeType='application/pdf'""")
            file_list = drive.ListFile({'q': query}).GetList()

            for file in file_list:
                if file['title'] == path.name:
                    file.InsertPermission({
                        'type': 'anyone',
                        'value': 'anyone',
                        'role': 'reader',
                    })

                    self.view.show_info(file['alternateLink'])

                    return

            self.view.show_info(
                f"File '{path.name}' not found "
                "in folder 'smth' on Google Drive")
        else:
            self.view.show_info('No notebooks found.')
