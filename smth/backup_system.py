import logging
import operator
import os
import sys

import fpdf
import sane

from smth import db
from smth import models
from smth import validators
from smth import views

log = logging.getLogger(__name__)


class BackupSystem:
    def __init__(self, view: views.CLIView, db_path: str):
        self._view = view

        try:
            self._db = db.DB(db_path)
        except db.Error as exception:
            self._handle_exception(exception)
            sys.exit(1)

    def scan(self) -> None:
        """Choose device, notebook and scan pages."""
        try:
            notebooks = self._db.get_notebook_titles()

            if not notebooks:
                self._view.show_info(
                    'No notebooks found. Create one with `smth create`.')
                return
        except db.Error as exception:
            self._handle_exception(exception)
            sys.exit(1)

        sane.init()

        self._view.show_info('Searching for available devices...')

        try:
            devices = list(map(operator.itemgetter(0), sane.get_devices()))
        except KeyboardInterrupt:
            log.info('No devices found due to keyboard interrupt')
            self._view.show_info('Scanning canceled.')
            return

        validator = validators.ScanPreferencesValidator()

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

            self._view.show_info('Creating PDF...')

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

    def _get_scanner(self, device: str) -> sane.SaneDev:
        scanner = sane.open(device)
        scanner.format = 'jpeg'
        scanner.mode = 'gray'
        scanner.resolution = 150
        return scanner

    def _get_pages_dir_path(self, notebook_title: str) -> str:
        pages_root = os.path.expanduser('~/.local/share/smth/pages')
        return os.path.join(pages_root, notebook_title)

    def _handle_exception(self, exception: Exception):
        log.exception(exception)
        self._view.show_error(str(exception))

