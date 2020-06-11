import logging
import pathlib
import sys
from typing import List

import fpdf
import PIL.Image as pillow

from smth import commands, config, db, models, scanner, validators, view

log = logging.getLogger(__name__)


class ScanCommand(commands.Command):  # pylint: disable=too-few-public-methods
    """Allows to scan a notebook."""

    def __init__(self, db_: db.DB, view_: view.View, conf: config.Config):
        self.db = db_
        self.view = view_
        self.conf = conf

    def execute(self, args: List[str] = None) -> None:
        """Ask user for scanning preferences, scan notebook and make PDF."""
        notebooks = []

        try:
            notebooks = self.db.get_notebook_titles()
        except db.Error as exception:
            log.exception(exception)
            self.view.show_error(str(exception))
            sys.exit(1)

        if not notebooks:
            message = 'No notebooks found. Create one with `smth create`.'
            self.view.show_info(message)
            return

        if args and '--set-device' in args:
            self.conf.scanner_device = ''

        scanner_ = scanner.Scanner(self.conf)
        scanner_.register(self.ScannerCallback(self.db, self.view, self.conf))

        validator = validators.ScanPreferencesValidator()
        answers = self.view.ask_for_scan_prefs(notebooks, validator)

        prefs = scanner.ScanPreferences()

        if not answers['notebook']:
            self.view.show_error('No notebook chosen.')
            sys.exit(1)

        try:
            prefs.notebook = self.db.get_notebook_by_title(answers['notebook'])

        except db.Error as exception:
            self.view.show_error(str(exception))
            log.exception(exception)
            sys.exit(1)

        for i in range(0, int(answers['append'])):
            page = (prefs.notebook.first_page_number +
                    prefs.notebook.total_pages + i)

            prefs.pages_queue.append(page)

        try:
            scanner_.scan(prefs)

        except scanner.Error as exception:
            self.view.show_error(f'{exception}.')
            log.exception(exception)
            sys.exit(1)

    class ScannerCallback(scanner.Callback):
        def __init__(self, db_: db.DB, view_: view.View, conf: config.Config):
            self.db = db_
            self.view = view_
            self.conf = conf

        def on_set_device(self):
            self.view.show_info('Searching for available devices...')

            try:
                devices = scanner.Scanner.get_devices()
                device = self.view.ask_for_device(devices)
                self.conf.scanner_device = device

            except scanner.Error as exception:
                self.view.show_error(f'Scanner error: {exception}.')
                log.exception(exception)
                sys.exit(1)

        def on_start(self, device_name: str, pages_queue: List[int]) -> None:
            self.view.show_info(f"Using device '{device_name}'.")

            pages_to_scan = ', '.join(list(map(str, pages_queue)))
            self.view.show_info(
                f"The following pages will be scanned: {pages_to_scan}.")

        def on_start_scan_page(self, page: int) -> None:
            self.view.show_info(f'Scanning page {page}...')

        def on_finish_scan_page(
                self, notebook: models.Notebook, page: int,
                image: pillow.Image) -> None:
            page_path = self._get_page_path(notebook, page)

            image.save(str(page_path))

            self.view.show_info(f'Page {page} saved at {page_path}')
            log.info("Scanned page %s of '%s'", page, notebook.title)

        def on_finish(self, notebook: models.Notebook):
            self.db.save_notebook(notebook)

            self.view.show_info('Creating PDF...')

            pdf = fpdf.FPDF(
                unit='pt',
                format=[notebook.type.page_width, notebook.type.page_height])

            for i in range(0, notebook.total_pages):
                page = notebook.first_page_number + i
                page_path = self._get_page_path(notebook, page)
                pdf.add_page()
                pdf.image(
                    str(page_path), 0, 0,
                    notebook.type.page_width, notebook.type.page_height)

            pdf.output(notebook.path, 'F')

            self.view.show_info(f"PDF saved at '{notebook.path}'.")

            self.view.show_info('Done.')

        def on_error(self, message):
            self.view.show_error(f'Scanner error: {message}.')
            log.error('Scanner error: %s.', message)
            sys.exit(1)

        def _get_page_path(
                self, notebook: models.Notebook, page: int) -> pathlib.Path:
            pages_root = pathlib.Path('~/.local/share/smth/pages').expanduser()
            return pages_root / notebook.title / f'{page}.jpg'
