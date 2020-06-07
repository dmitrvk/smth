from typing import List

from smth import models
from smth import views

class ListView(views.BaseView):
    """A view that shows a list of notebooks."""

    def show_notebooks(self, notebooks: List[models.Notebook]) -> None:
        """Show list of notebooks or message if no notebooks found."""
        if notebooks != None and len(notebooks) > 0:
            print('All notebooks:')
            for n in notebooks:
                if n.total_pages == 1:
                    print(f'  {n.title}  {n.total_pages} page  ({n.type.title})')
                else:
                    print(f'  {n.title}  {n.total_pages} pages  ({n.type.title})')
        else:
            print('No notebooks found.')
