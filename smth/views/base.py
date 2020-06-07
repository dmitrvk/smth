import sys
from typing import List

import PyInquirer as inquirer


class BaseView:
    """"User interface base class."""

    PROMPT_STYLE = inquirer.style_from_dict({
        inquirer.Token.QuestionMark: '#673ab7',
        inquirer.Token.Selected: '#673ab7',
        inquirer.Token.Pointer: '#673ab7',
    })

    def show_info(self, message: str) -> None:
        """Print message to stdout."""
        print(message)

    def show_error(self, message: str) -> None:
        """Print message to stderr."""
        print(message, file=sys.stderr)

    def _prompt(self, questions: List[dict]) -> dict:
        return inquirer.prompt(questions, style=self.PROMPT_STYLE)
