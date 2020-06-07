from typing import Dict, List

import inquirer

from smth import models, validators, views


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
