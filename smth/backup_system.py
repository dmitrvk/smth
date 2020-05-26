import logging
import os
import pathlib
import sys
from time import sleep

import fpdf
import inquirer
import sane

from .db import DB
from .db_error import DBError
from .validators import NotebookValidator

log = logging.getLogger(__name__)


class BackupSystem:
    def __init__(self):
        try:
            self._db = DB()
            self._notebooks = self._db.get_notebooks()

            if not self._db.notebook_type_exists('A4'):
                self._db.create_notebook_type('A4', 210, 297, False)

            self._notebook_types = self._db.get_notebook_types()
        except DBError as e:
            self._print_exception(e)
            sys.exit(1)

    def list(self) -> None:
        """Print list of all notebooks or notebook types."""
        if self._notebooks != None and len(self._notebooks) > 0:
            print('All notebooks:')
            for notebook in self._notebooks:
                print(f'  {notebook.title}  {notebook.total_pages} pages  '
                    f'({notebook.type.title})')
        else:
            print('No notebooks found.')

    def create(self) -> None:
        """Create notebook with given title, type, path and 1st page number."""
        try:
            validator = NotebookValidator(self._db)

            questions = [
                inquirer.Text(
                    name='title',
                    message='Enter title',
                    validate=validator.validate_title),
                inquirer.List(
                    name='type',
                    message='Choose type',
                    choices=list(map(lambda t: t.title, self._notebook_types)),
                    validate=validator.validate_type),
                inquirer.Path(
                    name='path',
                    message='Enter path to PDF',
                    path_type=inquirer.Path.FILE,
                    exists=False,
                    normalize_to_absolute_path=True,
                    validate=validator.validate_path),
                inquirer.Text(
                    name='first_page_number',
                    message='Enter 1st page number',
                    default=1,
                    validate=validator.validate_first_page_number)
            ]
            answers = inquirer.prompt(questions)

            answers['title'] = answers['title'].strip()
            answers['type'] = answers['type'].strip()
            answers['path'] = self._expand_path(answers['path'])
            answers['first_page_number'] = answers['first_page_number'].strip()

            self._create_empty_pdf(answers['path'])
            self._db.create_notebook(answers)

            pages_root = os.path.expanduser(f'~/.local/share/smth/pages')
            pages_dir = os.path.join(pages_root, answers['title'])
            pathlib.Path(pages_dir).mkdir(parents=True)

            log.info("Create notebook '{}' of type '{}' at '{}'".format(
                answers['title'], answers['type'], answers['path']))
            print("Create notebook '{}' of type '{}' at '{}'".format(
                answers['title'], answers['type'], answers['path']))

        except (DBError, OSError, ValueError) as e:
            self._print_exception(e)
            sys.exit(1)

    def types(self) -> None:
        """Print list of all notebook types."""
        if self._notebook_types != None and len(self._notebook_types) > 0:
            print('All notebook types:')
            for _type in self._notebook_types:
                print(f'  {_type.title}  '
                    f'{_type.page_width}x{_type.page_height}mm')
        else:
            print('No types found.')

    def scan(self) -> None:
        """Choose device, notebook and scan pages."""
        sane.init()

        print('Searching for available devices...')
        devices = sane.get_devices()

        questions = [
            inquirer.List(
                name='device',
                message='Choose device',
                choices=list(map(lambda d: d[0], devices))),
            inquirer.List(
                name='notebook',
                message='Choose notebook',
                choices=list(map(lambda n: n.title, self._notebooks)),
                carousel=True),
            inquirer.Text(
                name='append',
                message='Enter number of pages to append (or leave empty)')
        ]

        answers = inquirer.prompt(questions)

        answers['append'] = answers['append'].strip()

        if len(answers['append']) > 0:
            number_of_pages_to_append = int(answers['append'].strip())
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
                    print(f'Scanning page {page}...')
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

                print(f"PDF saved at '{notebook.path}'.")

                print('Done.')
            else:
                print('Nothing to scan.')
        else:
            print('Nothing to scan.')

    def _expand_path(self, path: str) -> str:
        """Return full absolute path."""
        path = str(path).strip()
        path = os.path.expandvars(os.path.expanduser(path))
        return os.path.abspath(path)

    def _create_empty_pdf(self, path: str) -> str:
        pdf = fpdf.FPDF()
        pdf.add_page()
        pdf.output(path)

    def _print_exception(self, exception: Exception):
        log.exception(exception)
        print(exception, file=sys.stderr)

