import sys
from typing import Dict, List

import PyInquirer as inquirer

from smth import models
from smth import validators


class View:
    """"User interface base class."""

    PROMPT_STYLE = inquirer.style_from_dict({
        inquirer.Token.QuestionMark: '#673ab7',
        inquirer.Token.Selected: '#673ab7',
        inquirer.Token.Pointer: '#673ab7',
    })

    Answers = Dict[str, str]

    def ask_for_new_notebook_info(
            self, types: List[str],
            validator: validators.NotebookValidator) -> Answers:
        """Ask user for notebook parameters and return answers.

        Validate answers with given validator.
        `types` should be only titles, not actual NotebookType objects."""
        questions = [
            {
                'type': 'input',
                'name': 'title',
                'message': 'Enter title:',
                'validate': validator.validate_title,
            },
            {
                'type': 'list',
                'name': 'type',
                'message': 'Choose type',
                'choices': types,
                'validate': validator.validate_type,
            },
            {
                'type': 'input',
                'name': 'path',
                'message': 'Enter path to PDF:',
                'validate': validator.validate_path,
            },
            {
                'type': 'input',
                'name': 'first_page_number',
                'message': 'Enter 1st page number:',
                'default': '1',
                'validate': validator.validate_first_page_number,
            },
        ]

        return self._prompt(questions)

    def ask_for_device(self, devices: List[str]) -> str:
        """Show list of devices and let user choose one."""
        questions = [
            {
                'type': 'list',
                'name': 'device',
                'message': 'Choose device',
                'choices': sorted(devices),
            },
        ]

        answers = self._prompt(questions)

        if answers:
            return answers.get('device', '')
        else:
            return ''

    def ask_for_scan_prefs(
            self, notebooks: List[str],
            validator: validators.ScanPreferencesValidator) -> Answers:
        """Ask user for notebook parameters and return dict with answers.

        Validate answers with given validator."""
        questions = [
            {
                'type': 'list',
                'name': 'notebook',
                'message': 'Choose notebook',
                'choices': notebooks,
            },
            {
                'type': 'input',
                'name': 'append',
                'message': 'How many new pages? (leave empty if none)',
                'validate': validator.validate_number_of_pages_to_append,
            },
        ]

        answers = self._prompt(questions)

        if answers:
            answers['notebook'] = answers['notebook'].strip()

            if answers['append']:
                answers['append'] = answers['append'].strip()
            else:
                answers['append'] = '0'

            return answers
        else:
            return {
                'notebook': '',
                'append': '0',
            }

    def show_notebooks(self, notebooks: List[models.Notebook]) -> None:
        """Show list of notebooks or message if no notebooks found."""
        if notebooks and len(notebooks) > 0:
            print('All notebooks:')
            for n in notebooks:
                type = n.type.title

                if n.total_pages == 1:
                    print(f'  {n.title}  {n.total_pages} page  ({type})')
                else:
                    print(f'  {n.title}  {n.total_pages} pages  ({type})')
        else:
            print('No notebooks found.')

    def show_types(self, types: List[models.NotebookType]) -> None:
        """Show list of notebook types or message if no types found."""
        if types and len(types) > 0:
            print('All notebook types:')
            for t in types:
                print(f'  {t.title}  {t.page_width}x{t.page_height}mm')
        else:
            print('No types found.')

    def show_info(self, message: str) -> None:
        """Print message to stdout."""
        print(message)

    def show_error(self, message: str) -> None:
        """Print message to stderr."""
        print(message, file=sys.stderr)

    def show_separator(self) -> None:  # pylint: disable=no-self-use
        """Print long line that divides sections of output."""
        print('----------------------------------------')

    def _prompt(self, questions: List[dict]) -> dict:
        return inquirer.prompt(questions, style=self.PROMPT_STYLE)
