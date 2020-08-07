# License: GNU GPL Version 3

"""The module provides `scan` command to perform scanning operations."""

import collections
import importlib.util
import logging
from typing import List

import fpdf
import PIL.Image as pillow

from smth import config, db, models, scanner, validators, view

from . import command, upload

log = logging.getLogger(__name__)


class ScanCommand(command.Command):  # pylint: disable=too-few-public-methods
    """Scans a notebook."""

    def __init__(self, db_: db.DB, view_: view.View):
        super().__init__(db_, view_)

        try:
            self.conf = config.Config()
        except config.Error as exception:
            self.exit_with_error(exception)

    def execute(self, args: List[str] = None) -> None:
        """Asks user for scanning preferences, scans notebook and makes PDF."""
        notebook_titles = self.get_notebook_titles_from_db()

        if not notebook_titles:
            message = 'No notebooks found. Create one with `smth create`.'
            self._view.show_info(message)
            return

        callback = ScanCommand.ScannerCallback(
            self, self._db, self._view, self.conf)
        callback.on_error = self.exit_with_error

        if args:
            if '--set-device' in args:
                try:
                    self.conf.scanner_device = ''
                except config.Error as exception:
                    self.exit_with_error(exception)

            if '--pdf-only' in args:
                title = self._view.ask_for_notebook(notebook_titles)

                if title:
                    try:
                        notebook = self._db.get_notebook_by_title(title)
                        callback.on_finish(notebook)
                        return
                    except db.Error as exception:
                        self.exit_with_error(exception)
                else:
                    return

        scanner_ = scanner.Scanner(self.conf, callback)
        notebook = self._get_notebook_to_scan(notebook_titles)
        pages_queue = self._get_pages_queue(notebook)
        scanner_.scan(notebook, pages_queue)

    class ScannerCallback(scanner.Callback):
        """Callback implementation defining what to do on scanner events."""

        def __init__(
                self, command_: command.Command,
                db_: db.DB, view_: view.View, conf: config.Config):
            self._command = command_
            self._db = db_
            self._view = view_
            self.conf = conf

        def on_searching_for_devices(self):
            self._view.show_info('Searching for available devices...')

        def on_set_device(self, devices: List[scanner.Device]):
            """Asks for device and retuns the device name chosen by the user.

            See the base class."""
            return self._view.ask_for_device(devices)

        def on_start(self, device_name: str, pages_queue: List[int]) -> None:
            """Shows the pages that will be scanned and asks for confirmation.

            See the base class.
            """
            self._view.show_separator()
            self._view.show_info(f"Using device '{device_name}'.")

            self._view.show_separator()

            pages_to_scan = ', '.join(list(map(str, pages_queue)))
            self._view.show_info(
                f"The following pages will be scanned: {pages_to_scan}.")

            if not self._view.confirm('Continue?', default_yes=True):
                self.on_error('Scanning cancelled.')

        def on_start_scan_page(self, page: int) -> None:
            """See the base class."""
            self._view.show_info(f'Scanning page {page}...')

        def on_finish_scan_page(
                self, notebook: models.Notebook, page: int,
                image: pillow.Image) -> None:
            """Saves scanned page to notebook's pages directory.

            See the base class."""
            page_path = notebook.get_page_path(page)
            image.save(str(page_path))

            self._view.show_info(f'Page {page} saved at {page_path}')
            log.info("Scanned page %s of '%s'", page, notebook.title)

        def on_finish(self, notebook: models.Notebook):
            """Saves the notebook in the databasee and creates PDF file.

            If PyDrive is installed and `ask_upload` config parameter is True,
            asks whether the user wants to upload the notebook to Google Drive.

            See the base class.
            """
            self._db.save_notebook(notebook)

            self._view.show_separator()
            self._view.show_info('Creating PDF...')

            pdf_page_size = [
                int(notebook.type.page_width * 150 / 25.4),
                int(notebook.type.page_height * 150 / 25.4),
            ]

            if notebook.type.pages_paired:
                pdf_page_size[0] *= 2

            pdf = fpdf.FPDF(unit='pt', format=pdf_page_size)

            for i in range(0, notebook.total_pages):
                page = notebook.first_page_number + i

                if notebook.type.pages_paired:
                    if notebook.first_page_number % 2 == page % 2:
                        # left page
                        pdf.add_page()
                        pdf.image(
                            str(notebook.get_page_path(page)),
                            0, 0,
                            int(pdf_page_size[0] / 2), pdf_page_size[1])
                    else:
                        # right page
                        pdf.image(
                            str(notebook.get_page_path(page)),
                            int(pdf_page_size[0] / 2), 0,
                            int(pdf_page_size[0] / 2), pdf_page_size[1])
                else:
                    pdf.add_page()
                    pdf.image(
                        str(notebook.get_page_path(page)),
                        0, 0,
                        pdf_page_size[0], pdf_page_size[1])

            pdf.output(notebook.path)

            self._view.show_info(f"PDF saved at '{notebook.path}'.")
            self._view.show_separator()

            try:
                if (importlib.util.find_spec('pydrive') and
                        self.conf.scanner_ask_upload):
                    if self._view.confirm('Upload notebook to Google Drive?'):
                        command = upload.UploadCommand(self._db, self._view)
                        args = [notebook.title]
                        command.execute(args)
            except config.Error as exception:
                self._view.show_error(f'Config file error: {str(exception)}')

            self._view.show_info('Done.')

        def on_error(self, message):
            """See the base class."""

    def _get_notebook_to_scan(
            self, notebook_titles: List[str]) -> models.Notebook:
        """Asks for notebook and returns the user's choice.

        Args:
            notebook_titles:
                A list of all notebooks' titles to choose from.
        """
        notebook_title = self._view.ask_for_notebook(notebook_titles)

        if not notebook_title:
            self.exit_with_error('No notebook chosen.')

        try:
            return self._db.get_notebook_by_title(notebook_title)
        except db.Error as exception:
            self.exit_with_error(exception)

    def _get_pages_queue(self, notebook: models.Notebook) -> collections.deque:
        """Asks for pages which should be appended and/or replaced."""
        pages_queue = collections.deque()

        validator = validators.PagesToScanValidator(notebook)
        append = self._view.ask_for_pages_to_append(validator)

        if notebook.total_pages > 0:
            replace_answer = self._view.ask_for_pages_to_replace(validator)

            replace = []
            for item in replace_answer:
                if '-' in item:
                    range_start, range_end = map(int, item.split('-'))
                    replace.extend(list(range(range_start, range_end + 1)))
                else:
                    replace.append(int(item))
            replace = list(set(replace))  # Remove duplicates
            replace.sort()
            pages_queue.extend(replace)

        for i in range(0, append):
            page = (notebook.first_page_number + notebook.total_pages + i)
            pages_queue.append(page)

        return pages_queue
