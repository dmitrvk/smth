import configparser
import logging
import operator
import pathlib
import sys

import fpdf
import sane

from smth import db
from smth import main
from smth import models
from smth import validators
from smth import views

log = logging.getLogger(__name__)


class ScanController:
    """Allows to scan a notebook."""

    def __init__(self, db_path: str, config: configparser.ConfigParser):
        self.db_path = db_path
        self.config = config

    def scan_notebook(self) -> None:
        """Ask user for scanning preferences, scan notebook and make PDF."""
        view = views.ScanView()

        try:
            db_ = db.DB(self.db_path)
            notebooks = db_.get_notebook_titles()

            if not notebooks:
                message = 'No notebooks found. Create one with `smth create`.'
                view.show_info(message)
                return
        except db.Error as exception:
            log.exception(exception)
            view.show_error(str(exception))
            sys.exit(1)

        sane.init()
        scanner = None
        devices = None

        if self.config.has_option('scanner', 'device'):
            device = self.config['scanner']['device']
            scanner = self._get_scanner(device)
            view.show_info(f"Using device '{device}'.")
        else:
            view.show_info('Searching for available devices...')

            try:
                devices = list(map(operator.itemgetter(0), sane.get_devices()))
            except KeyboardInterrupt:
                log.info('No devices found due to keyboard interrupt')
                view.show_info('Scanning canceled.')
                return

        validator = validators.ScanPreferencesValidator()
        answers = view.ask_for_scan_prefs(devices, notebooks, validator)

        if not answers:
            log.info('Scan did not start due to keyboard interrupt')
            view.show_info('Scanning canceled.')
            return
        elif 'device' in answers:
            self.config['scanner'] = {}
            self.config['scanner']['device'] = answers['device']

            with open(str(main.CONFIG_PATH), 'w') as config_file:
                self.config.write(config_file)

        answers['append'] = answers['append'].strip()

        append = int(answers['append']) if len(answers['append']) > 0 else 0

        if append <= 0:
            view.show_info('Nothing to scan.')
        else:
            notebook = db_.get_notebook_by_title(answers['notebook'])
            pages_dir_path = self._get_pages_dir_path(notebook.title)

            if not scanner:
                scanner = self._get_scanner(answers['device'])

            for i in range(0, append):
                page = notebook.first_page_number + notebook.total_pages + i

                view.show_info(f'Scanning page {page}...')

                page_path = pages_dir_path.joinpath(f'{page}.jpg')

                try:
                    image = scanner.scan()
                    image.save(str(page_path))
                    log.info(f"Scanned page {page} of '{notebook.title}'")
                except KeyboardInterrupt:
                    log.info('Scan interrupted by user.')
                    view.show_info('Scanning canceled.')
                    scanner.close()
                    return

            scanner.close()

            notebook.total_pages += append
            db_.save_notebook(notebook)

            view.show_info('Creating PDF...')

            width, height = image.size
            pdf = fpdf.FPDF(unit='pt', format=[width, height])

            for i in range(0, notebook.total_pages):
                page = notebook.first_page_number + i
                page_path = pages_dir_path.joinpath(f'{page}.jpg')
                pdf.add_page()
                pdf.image(str(page_path), 0, 0, width, height)

            pdf.output(notebook.path, 'F')

            view.show_info(f"PDF saved at '{notebook.path}'.")
            view.show_info('Done.')

    def _get_scanner(self, device: str) -> sane.SaneDev:
        scanner = sane.open(device)
        scanner.format = 'jpeg'
        scanner.mode = 'gray'
        scanner.resolution = 150
        return scanner

    def _get_pages_dir_path(self, notebook_title: str) -> pathlib.Path:
        pages_root = pathlib.Path('~/.local/share/smth/pages').expanduser()
        return pages_root.joinpath(notebook_title)
