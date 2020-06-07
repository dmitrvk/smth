from typing import List

from smth import models, views


class ListView(views.BaseView):
    """A view that shows a list of notebooks."""

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
