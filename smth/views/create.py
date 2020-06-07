from typing import Dict, List

from smth import views
from smth.controllers import validators


class CreateView(views.BaseView):
    """A view that asks user for needed info when creating a notebook."""

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
