import operator
import sys
from typing import Any, Dict, List

import PyInquirer as inquirer

from smth import models, scanner, validators

Answers = Dict[str, Any]


class View:
    """"User interface base class."""

    PROMPT_STYLE = inquirer.style_from_dict({
        inquirer.Token.QuestionMark: '#673ab7',
        inquirer.Token.Selected: '#673ab7',
        inquirer.Token.Pointer: '#673ab7',
    })

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

        answers = self._prompt(questions)

        if answers:
            answers['title'] = answers['title'].strip()
            answers['type'] = answers['type'].strip()
            answers['path'] = answers['path'].strip()
            answers['first_page_number'] = int(answers['first_page_number'])
            return answers

        return {}

    def ask_for_device(self, devices: List[scanner.Device]) -> str:
        """Show list of devices and let user choose one. Return device name."""
        def prepare_choices(devices: List[scanner.Device]) -> List[str]:
            """Prepare device choices for user."""
            choices = []

            for dev in devices:
                choices.append(
                    f'{dev.name} ({dev.vendor} {dev.model} {dev.type})')

            choices.sort()
            return choices

        def extract_device_name_from_choice(choice: str) -> str:
            """Return only device name from formatted string."""
            if choice:
                return choice.split('(')[0].rstrip()

            return ''

        devices.sort(key=operator.attrgetter('name'))

        choices = prepare_choices(devices)

        questions = [
            {
                'type': 'list',
                'name': 'device',
                'message': 'Choose device',
                'choices': choices,
            },
        ]

        answers = self._prompt(questions)

        if answers:
            return extract_device_name_from_choice(answers.get('device', ''))

        return ''

    def ask_for_notebook_to_scan(self, notebooks: List[str]) -> str:
        """Ask for notebook which user wants to scan and return its title."""
        questions = [
            {
                'type': 'list',
                'name': 'notebook',
                'message': 'Choose notebook',
                'choices': notebooks,
            },
        ]

        answers = self._prompt(questions)

        if answers:
            return answers['notebook'].strip()

        return ''

    def ask_for_pages_to_append(
            self, validator: validators.ScanPreferencesValidator) -> int:
        """Ask user for number of pages user wants to append to a notebook.

        Validate answers with given validator."""
        questions = [
            {
                'type': 'input',
                'name': 'append',
                'message': 'How many new pages? (leave empty if none)',
                'validate': validator.validate_number_of_pages_to_append,
            },
        ]

        answers = self._prompt(questions)

        if answers:
            if answers['append']:
                return int(answers['append'].strip())

            return 0

        return 0

    def ask_for_pages_to_replace(
            self, validator: validators.ScanPreferencesValidator) -> List[str]:
        """Ask user for notebook parameters and return dict with answers.

        Validate answers with given validator."""
        questions = [
            {
                'type': 'input',
                'name': 'replace',
                'message': 'What pages to replace? (leave empty if none)',
                'validate': validator.validate_pages_to_replace,
            },
        ]

        answers = self._prompt(questions)

        if answers:
            replace = answers['replace'].strip().split()
            replace = list(map(operator.methodcaller('strip'), replace))
            replace = list(filter(lambda s: s != '', replace))
            return replace

        return []

    def show_notebooks(self, notebooks: List[models.Notebook]) -> None:  # pylint: disable=no-self-use  # noqa: E501
        """Show list of notebooks or message if no notebooks found."""
        if notebooks and len(notebooks) > 0:
            print('All notebooks:')
            for notebook in notebooks:
                type_ = notebook.type.title

                if notebook.total_pages == 1:
                    print(f'  {notebook.title}  '
                          f'{notebook.total_pages} page  ({type_})')
                else:
                    print(f'  {notebook.title}  '
                          f'{notebook.total_pages} pages  ({type_})')
        else:
            print('No notebooks found.')

    def show_types(self, types: List[models.NotebookType]) -> None:  # pylint: disable=no-self-use  # noqa: E501
        """Show list of notebook types or message if no types found."""
        if types and len(types) > 0:
            print('All notebook types:')
            for type_ in types:
                print(f'  {type_.title}  '
                      f'{type_.page_width}x{type_.page_height}mm')
        else:
            print('No types found.')

    def show_info(self, message: str) -> None:  # pylint: disable=no-self-use
        """Print message to stdout."""
        print(message)

    def show_error(self, message: str) -> None:  # pylint: disable=no-self-use
        """Print message to stderr."""
        print(message, file=sys.stderr)

    def show_separator(self) -> None:  # pylint: disable=no-self-use
        """Print long line that divides sections of output."""
        print('----------------------------------------')

    def _prompt(self, questions: List[dict]) -> dict:
        return inquirer.prompt(questions, style=self.PROMPT_STYLE)
