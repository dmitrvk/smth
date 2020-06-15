import logging
from typing import List

import fpdf
import PIL.Image as pillow

from smth import config, db, models, scanner, validators, view

from . import command

log = logging.getLogger(__name__)


class ScanCommand(command.Command):  # pylint: disable=too-few-public-methods
    """Allows to scan a notebook."""

    def __init__(self, db_: db.DB, view_: view.View, conf: config.Config):
        super().__init__(db_, view_)
        self.conf = conf

    def execute(self, args: List[str] = None) -> None:
        """Ask user for scanning preferences, scan notebook and make PDF."""
        notebooks = []

        try:
            notebooks = self._db.get_notebook_titles()
        except db.Error as exception:
            self._exit_with_error(exception)

        if not notebooks:
            message = 'No notebooks found. Create one with `smth create`.'
            self.view.show_info(message)
            return

        if args and '--set-device' in args:
            self.conf.scanner_device = ''

        scanner_ = scanner.Scanner(self.conf)
        scanner_.register(self.ScannerCallback(
            self, self._db, self.view, self.conf))

        prefs = self._make_scan_prefs(notebooks)

        try:
            scanner_.scan(prefs)

        except scanner.Error as exception:
            self._exit_with_error(exception)

    class ScannerCallback(scanner.Callback):
        """Callback implementation defining what to do on scanner events."""

        def __init__(
                self, command_: command.Command,
                db_: db.DB, view_: view.View, conf: config.Config):
            self._command = command_
            self._db = db_
            self.view = view_
            self.conf = conf

        def on_set_device(self):
            self.view.show_info('Searching for available devices...')

            try:
                devices = scanner.Scanner.get_devices()
                device_name = self.view.ask_for_device(devices)
                self.conf.scanner_device = device_name

            except scanner.Error as exception:
                self.on_error(str(exception))

        def on_start(self, device_name: str, pages_queue: List[int]) -> None:
            self.view.show_separator()
            self.view.show_info(f"Using device '{device_name}'.")

            self.view.show_separator()

            pages_to_scan = ', '.join(list(map(str, pages_queue)))
            self.view.show_info(
                f"The following pages will be scanned: {pages_to_scan}.")

        def on_start_scan_page(self, page: int) -> None:
            self.view.show_info(f'Scanning page {page}...')

        def on_finish_scan_page(
                self, notebook: models.Notebook, page: int,
                image: pillow.Image) -> None:
            page_path = notebook.get_page_path(page)
            image.save(str(page_path))

            self.view.show_info(f'Page {page} saved at {page_path}')
            log.info("Scanned page %s of '%s'", page, notebook.title)

        def on_finish(self, notebook: models.Notebook):
            self._db.save_notebook(notebook)

            self.view.show_separator()
            self.view.show_info('Creating PDF...')

            pdf = fpdf.FPDF(
                unit='pt',
                format=[
                    int(notebook.type.page_width * 150 / 25.4),
                    int(notebook.type.page_height * 150 / 25.4),
                ])

            for i in range(0, notebook.total_pages):
                page = notebook.first_page_number + i
                pdf.add_page()
                pdf.image(
                    str(notebook.get_page_path(page)), 0, 0,
                    int(notebook.type.page_width * 150 / 25.4),
                    int(notebook.type.page_height * 150 / 25.4))

            pdf.output(notebook.path, 'F')

            self.view.show_info(f"PDF saved at '{notebook.path}'.")
            self.view.show_separator()

            self.view.show_info('Done.')

        def on_error(self, message):
            self._command._exit_with_error(message)

    def _make_scan_prefs(
            self, notebooks: models.Notebook) -> scanner.ScanPreferences():
        prefs = scanner.ScanPreferences()

        notebook_title = self.view.ask_for_notebook_to_scan(notebooks)

        if not notebook_title:
            self._exit_with_error('No notebook chosen.')

        try:
            prefs.notebook = self._db.get_notebook_by_title(notebook_title)

        except db.Error as exception:
            self._exit_with_error(exception)

        validator = validators.ScanPreferencesValidator(prefs.notebook)
        append = self.view.ask_for_pages_to_append(validator)

        if prefs.notebook.total_pages > 0:
            replace_answer = self.view.ask_for_pages_to_replace(validator)

            replace = []
            for item in replace_answer:
                if '-' in item:
                    range_start, range_end = map(int, item.split('-'))
                    replace.extend(list(range(range_start, range_end + 1)))
                else:
                    replace.append(int(item))
            replace = list(set(replace))  # Remove duplicates
            replace.sort()
            prefs.pages_queue.extend(replace)

        for i in range(0, append):
            page = (prefs.notebook.first_page_number +
                    prefs.notebook.total_pages + i)

            prefs.pages_queue.append(page)

        return prefs
