import sys
from typing import Dict, List

import inquirer

from smth import validators


class CLIView:
    """User interface."""

    Answers = Dict[str, str]

    def show_notebooks(self, notebooks: list) -> None:
        """Show list of notebooks or message if no notebooks found."""
        if notebooks != None and len(notebooks) > 0:
            print('All notebooks:')
            for n in notebooks:
                print(f'  {n.title}  {n.total_pages} pages  ({n.type.title})')
        else:
            print('No notebooks found.')

    def show_types(self, types: list) -> None:
        """Show list of notebook types or message if no types found."""
        if types != None and len(types) > 0:
            print('All notebook types:')
            for t in types:
                print(f'  {t.title}  {t.page_width}x{t.page_height}mm')
        else:
            print('No types found.')

    def ask_for_new_notebook_info(
            self, types: List[str],
            validator: validators.NotebookValidator) -> Answers:
        """Ask user for notebook parameters and return answers.

        Validate answers with given validator.
        `types` should be only titles, not actual NotebookType objects."""
        questions = [
            inquirer.Text(
                name='title',
                message='Enter title',
                validate=validator.validate_title),
            inquirer.List(
                name='type',
                message='Choose type',
                choices=types,
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

        return inquirer.prompt(questions)

    def ask_for_scan_prefs(
            self, devices: List[str], notebooks: List[str],
            validator: validators.ScanPreferencesValidator) -> Answers:
        """Ask user for notebook parameters and return dict with answers.

        Validate answers with given validator."""
        questions = [
            inquirer.List(
                name='device',
                message='Choose device',
                choices=devices),
            inquirer.List(
                name='notebook',
                message='Choose notebook',
                choices=notebooks,
                carousel=True),
            inquirer.Text(
                name='append',
                message='How many new pages? (leave empty if none)',
                validate=validator.validate_number_of_pages_to_append)
        ]

        return inquirer.prompt(questions)

    def show_info(self, message: str) -> None:
        """Print message to stdout."""
        print(message)

    def show_error(self, message: str) -> None:
        """Print message to stderr."""
        print(message, file=sys.stderr)

