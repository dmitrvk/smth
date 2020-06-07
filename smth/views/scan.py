from typing import Dict, List

from smth import views
from smth.controllers import validators


class ScanView(views.BaseView):
    """The view asks for scanning preferences and shows scanning progress."""

    Answers = Dict[str, str]

    def ask_for_scan_prefs(
            self, devices: List[str], notebooks: List[str],
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

        if devices:
            questions.insert(0, {
                'type': 'list',
                'name': 'device',
                'message': 'Choose device',
                'choices': sorted(devices),
            })

        return self._prompt(questions)
