# License: GNU GPL Version 3

"""This module contains the View class which is used to interact with user.

PyInquirer library is used to create the user interface.

    Typical usage example:

    notebooks_titles = ['notebook1', 'notebook2']
    view_ = view.View()
    chosen_notebook = view_.ask_for_notebook(notebooks)
"""

import operator
import sys
from typing import Any, Dict, List

import PyInquirer as inquirer

from smth import models, scanner, validators

Answers = Dict[str, Any]


class View:
    """"User interface base class."""

    PROMPT_STYLE = inquirer.style_from_dict({})

    def ask_for_new_notebook_info(
            self, types: List[str],
            validator: validators.NotebookValidator) -> Answers:
        """Asks user for notebook parameters and returns answers.

        Args:
            types:
                Notebook types' titles to choose from.
            validator:
                Validator for user input.

        Returns:
            A dict mapping questions' names to corresponding answers.
        """
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

    def ask_for_updated_notebook_properties(
            self, notebook: models.Notebook,
            validator: validators.NotebookUpdateValidator) -> Answers:
        """Ask user for updated notebook parameters and return answers.

        Args:
            notebook:
                Notebook to update.  Used here to display current notebook's
                properties.
            validator:
                Validator for user input.

        Returns:
            A dict mapping questions' names to corresponding answers.
        """
        questions = [
            {
                'type': 'input',
                'name': 'title',
                'message': 'Enter title:',
                'default': notebook.title,
                'validate': validator.validate_title,
            },
            {
                'type': 'input',
                'name': 'path',
                'message': 'Enter path to PDF:',
                'default': str(notebook.path),
                'validate': validator.validate_path,
            },
        ]

        answers = self._prompt(questions)

        if answers:
            answers['title'] = answers['title'].strip()
            answers['path'] = answers['path'].strip()
            return answers

        return {}

    def ask_for_new_type_info(
            self, validator: validators.TypeValidator) -> Answers:
        """Ask user for notebook parameters and return answers.

        Args:
            validator:
                Validator for user input.

        Returns:
            A dict mapping questions' names to corresponding answers.
        """
        questions = [
            {
                'type': 'input',
                'name': 'title',
                'message': 'Enter title:',
                'validate': validator.validate_title,
            },
            {
                'type': 'input',
                'name': 'page_width',
                'message': 'Enter page width in millimeters:',
                'validate': validator.validate_page_size,
            },
            {
                'type': 'input',
                'name': 'page_height',
                'message': 'Enter page height in millimeters:',
                'validate': validator.validate_page_size,
            },
            {
                'type': 'confirm',
                'name': 'pages_paired',
                'message': 'Are pages paired? (default - no)',
                'default': False,
            },
        ]

        answers = self._prompt(questions)

        if answers:
            answers['title'] = answers['title'].strip()
            answers['page_width'] = int(answers['page_width'])
            answers['page_height'] = int(answers['page_height'])
            return answers

        return {}

    def ask_for_device(self, devices: List[scanner.Device]) -> str:
        """Shows list of devices to choose one from.

        Args:
            devices:
                A list of scanner devices.  Each device is represented as a
                named tuple of strings with device's name, vendor, model and
                type.

        Returns:
            A string with chosen device name.
        """
        def prepare_choices(devices: List[scanner.Device]) -> List[str]:
            """Forms strings from named tuples representing devices."""
            choices = []

            for dev in devices:
                choices.append(
                    f'{dev.name} ({dev.vendor} {dev.model} {dev.type})')

            choices.sort()
            return choices

        def extract_device_name_from_choice(choice: str) -> str:
            """Returns only device's name from formatted string."""
            return choice.split('(')[0].rstrip()

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

    def ask_for_notebook(self, notebooks: List[str]) -> str:
        """Asks for notebook and returns its title.

        Args:
            notebooks:
                A list of notebooks' titles.
        """
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

    def ask_for_type(self, types: List[str]) -> str:
        """Asks for notebook type and returns its title.

        Args:
            types:
                A list of notebook types' titles.
        """
        questions = [
            {
                'type': 'list',
                'name': 'type',
                'message': 'Choose type',
                'choices': types,
            },
        ]

        answers = self._prompt(questions)

        if answers:
            return answers['type'].strip()

        return ''

    def ask_for_pages_to_append(
            self, validator: validators.PagesToScanValidator) -> int:
        """Asks for a number of pages the user wants to append to a notebook.

        Args:
            validator:
                Validator for user input.

        Returns:
            A number of pages.
        """
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
            append = answers['append'].strip()

            if append:
                return int(append)

            return 0

        return 0

    def ask_for_pages_to_replace(
            self, validator: validators.PagesToScanValidator) -> List[str]:
        """Asks for pages the user wants to replace in a notebook.

        Args:
            validator:
                Validator for user input.

        Returns:
            A splitted string the user typed.  It should contain page numbers
            or ranges of pages.
        """
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
        """Shows the list of notebooks or a message if no notebooks found.

        Args:
            notebooks:
                A list of notebooks to show.  For each notebook the function
                prints its title, total number of pages and the information
                about its type - the type's title and the page size in
                millimeters.
        """
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
        """Shows the list of notebook types or a message if no types found.

        Args:
            types:
                A list of types to show.  For each type the function prints its
                title and the page size in millimeters.
        """
        if types and len(types) > 0:
            print('All notebook types:')
            for type_ in types:
                print(f'  {type_.title}  '
                      f'{type_.page_width}x{type_.page_height}mm')
        else:
            print('No types found.')

    def confirm(self, question: str, default_yes: bool = False) -> bool:  # pylint: disable=no-self-use  # noqa: E501
        """Asks for confirmation and returns the answer (yes/no question).

        To answer `Yes`, the user should press `y`.  To answer `No`, the user
        should press `n`.  If the user hits Enter, the default answer is
        accepted (`No` by default, but set to `Yes` if the `default_yes`
        argument is True).

        Args:
            question:
                A string with question.
            default_yes:
                Optional; If True, `Yes` is the default answer.  The default
                answer is `No` otherwise.

        Returns:
            True, if answered `Yes`; False, if answered `No`.
        """
        questions = [
            {
                'type': 'confirm',
                'name': 'answer',
                'message': question,
                'default': default_yes,
            },
        ]

        answers = self._prompt(questions)

        if answers:
            return answers['answer']

        return False

    def show_info(self, message: str) -> None:  # pylint: disable=no-self-use
        """Prints a string to stdout."""
        print(message)

    def show_error(self, message: str) -> None:  # pylint: disable=no-self-use
        """Prints a string to stderr."""
        print(message, file=sys.stderr)

    def show_separator(self) -> None:  # pylint: disable=no-self-use
        """Prints a long line that visually divides sections of output text."""
        print('----------------------------------------')

    def _prompt(self, questions: List[dict]) -> dict:
        return inquirer.prompt(questions, style=self.PROMPT_STYLE)
