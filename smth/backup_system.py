import logging
import os
import pathlib
import sys
from time import sleep

import fpdf
import sane

from smth.db import DB, DBError
from smth.validators import NotebookValidator, ScanPreferencesValidator
from smth.view import View

log = logging.getLogger(__name__)


class BackupSystem:
    def __init__(self, view: View):
        self._view = view

        try:
            self._db = DB(os.path.expanduser('~/.local/share/smth/smth.db'))
            self._notebooks = self._db.get_notebooks()

            if not self._db.notebook_type_exists('A4'):
                self._db.create_notebook_type('A4', 210, 297, False)

            self._notebook_types = self._db.get_notebook_types()
        except DBError as e:
            self._handle_exception(e)
            sys.exit(1)

    def list(self) -> None:
        """Print list of all notebooks."""
        self._view.show_list_of_notebooks(self._notebooks)

    def types(self) -> None:
        """Print list of all notebook types."""
        self._view.show_list_of_notebook_types(self._notebook_types)

    def create(self) -> None:
        """Create notebook with given title, type, path and 1st page number."""
        try:
            answers = self._view.ask_for_new_notebook_info(
                list(map(lambda t: t.title, self._notebook_types)),
                NotebookValidator(self._db))

            title = answers['title'].strip()
            type = answers['type'].strip()
            path = self._expand_path(answers['path'])
            first_page_number = answers['first_page_number'].strip()

            self._create_empty_pdf(path)
            self._db.create_notebook(answers)

            pages_root = os.path.expanduser(f'~/.local/share/smth/pages')
            pages_dir = os.path.join(pages_root, title)
            pathlib.Path(pages_dir).mkdir(parents=True)

            message = f"Create notebook '{title}' of type '{type}' at '{path}'"
            log.info(message)
            self._view.show_info(message)

        except (DBError, OSError) as e:
            self._handle_exception(e)
            sys.exit(1)

    def scan(self) -> None:
        """Choose device, notebook and scan pages."""
        sane.init()

        self._view.show_info('Searching for available devices...')
        devices = sane.get_devices()

        answers = self._view.ask_for_scan_preferences(
            list(map(lambda d: d[0], devices)),
            list(map(lambda n: n.title, self._notebooks)),
            ScanPreferencesValidator())

        answers['append'] = answers['append'].strip()

        if len(answers['append']) > 0:
            number_of_pages_to_append = int(answers['append'])
            if number_of_pages_to_append > 0:
                notebook = list(filter((lambda n: n.title == answers['notebook']),
                        self._notebooks))[0]

                scanner = sane.open(answers['device'])
                scanner.format = 'jpeg'
                scanner.mode = 'gray'
                scanner.resolution = 150

                pages_root = os.path.expanduser('~/.local/share/smth/pages')
                pages_dir = os.path.join(pages_root, notebook.title)

                for i in range(0, number_of_pages_to_append):
                    page = notebook.first_page_number + notebook.total_pages + i
                    self._view.show_info(f'Scanning page {page}...')
                    page_path = os.path.join(pages_dir, f'{page}.jpg')
                    image = scanner.scan()
                    image.save(page_path)

                scanner.close()

                notebook.total_pages += number_of_pages_to_append
                self._db.save_notebook(notebook)

                width, height = image.size
                pdf = fpdf.FPDF(unit='pt', format=[width, height])

                for i in range(0, notebook.total_pages):
                    page = notebook.first_page_number + i
                    page_path = os.path.join(pages_dir, f'{page}.jpg')
                    pdf.add_page()
                    pdf.image(page_path, 0, 0, width, height)

                pdf.output(notebook.path, 'F')

                self._view.show_info(f"PDF saved at '{notebook.path}'.")

                self._view.show_info('Done.')
            else:
                self._view.show_info('Nothing to scan.')
        else:
            self._view.show_info('Nothing to scan.')

    def _expand_path(self, path: str) -> str:
        """Return full absolute path."""
        path = str(path).strip()
        path = os.path.expandvars(os.path.expanduser(path))
        return os.path.abspath(path)

    def _create_empty_pdf(self, path: str) -> str:
        pdf = fpdf.FPDF()
        pdf.add_page()
        pdf.output(path)

    def _handle_exception(self, exception: Exception):
        log.exception(exception)
        self._view.show_error(str(exception))

