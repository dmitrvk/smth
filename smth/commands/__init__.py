# License: GNU GPL Version 3

"""The package contains classes that replesent different commands.

Each command is inherited from the abstract Command class and
can be executed with the execute() method like this:

    class NewCommand(commands.Command):
        def execute(self, args):
            ...

    command = NewCommand(db, view)
    command.execute(args)
"""

from .command import Command
from .create import CreateCommand
from .delete import DeleteCommand
from .list import ListCommand
from .open import OpenCommand
from .scan import ScanCommand
from .share import ShareCommand
from .types import TypesCommand
from .update import UpdateCommand
from .upload import UploadCommand

__all__ = [
    'Command', 'CreateCommand', 'DeleteCommand', 'ListCommand', 'OpenCommand',
    'ScanCommand', 'ShareCommand', 'TypesCommand', 'UpdateCommand',
    'UploadCommand'
]
