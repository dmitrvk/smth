import logging
import os
import pathlib
import sys
from operator import attrgetter, itemgetter
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
                log.info('Created A4 notebook type.')

            self._notebook_types = self._db.get_notebook_types()
        except DBError as exception:
            self._handle_exception(exception)
            sys.exit(1)

    def list(self) -> None:
        """Print list of all notebooks."""
        try:
            self._view.show_notebooks(self._db.get_notebooks())
        except DBError as exception:
            self._handle_exception(exception)
            sys.exit(1)

    def types(self) -> None:
        """Print list of all notebook types."""
        try:
            self._view.show_notebook_types(self._db.get_notebook_types())
        except DBError as exception:
            self._handle_exception(exception)
            sys.exit(1)

    def create(self) -> None:
        """Create notebook with given title, type, path and 1st page number."""
        try:
            types = self._db.get_notebook_types_titles()
            validator = NotebookValidator(self._db)

            answers = self._view.ask_for_new_notebook_info(types, validator)

            if not answers:
                log.info('Creation stopped due to keyboard interrupt')
                self._view.show_info('Nothing created.')
                return

            title = answers['title'].strip()
            type = answers['type'].strip()
            path = self._expand_path(answers['path'])
            first_page_number = answers['first_page_number'].strip()

            self._create_empty_pdf(path)
            self._db.create_notebook(title, type, path, first_page_number)

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

        try:
            devices = list(map(itemgetter(0), sane.get_devices()))
        except KeyboardInterrupt:
            log.info('No devices found due to keyboard interrupt')
            self._view.show_info('Scanning canceled.')
            return

        notebooks = list(map(attrgetter('title'), self._notebooks))
        validator = ScanPreferencesValidator()

        answers = self._view.ask_for_scan_prefs(devices, notebooks, validator)

        if not answers:
            log.info('Scan did not start due to keyboard interrupt')
            self._view.show_info('Scanning canceled.')
            return

        answers['append'] = answers['append'].strip()

        append = int(answers['append']) if len(answers['append']) > 0 else 0

        if append <= 0:
            self._view.show_info('Nothing to scan.')
        else:
            notebook = self._db.get_notebook_by_title(answers['notebook'])
            pages_dir = self._get_pages_dir_path(notebook.title)

            scanner = self._get_scanner(answers['device'])

            for i in range(0, append):
                page = notebook.first_page_number + notebook.total_pages + i

                self._view.show_info(f'Scanning page {page}...')

                page_path = os.path.join(pages_dir, f'{page}.jpg')

                try:
                    image = scanner.scan()
                    image.save(page_path)
                    log.info(f"Scanned page {page} of '{notebook.title}'")
                except KeyboardInterrupt:
                    log.info('Scan interrupted by user.')
                    self._view.show_info('Scanning canceled.')
                    scanner.close()
                    return

            scanner.close()

            notebook.total_pages += append
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

    def _expand_path(self, path: str) -> str:
        """Return full absolute path."""
        path = str(path).strip()
        path = os.path.expandvars(os.path.expanduser(path))
        return os.path.abspath(path)

    def _get_scanner(self, device: str) -> sane.SaneDev:
        scanner = sane.open(device)
        scanner.format = 'jpeg'
        scanner.mode = 'gray'
        scanner.resolution = 150
        return scanner

    def _get_pages_dir_path(self, notebook_title: str) -> str:
        pages_root = os.path.expanduser('~/.local/share/smth/pages')
        return os.path.join(pages_root, notebook_title)

    def _create_empty_pdf(self, path: str) -> None:
        pdf = fpdf.FPDF()
        pdf.add_page()
        pdf.output(path)
        log.info("Created empty PDF at '{path}'")

    def _handle_exception(self, exception: Exception):
        log.exception(exception)
        self._view.show_error(str(exception))

