from typing import List

from smth import models, views


class TypesView(views.BaseView):
    """A view that shows a list of notebook types."""

    def show_types(self, types: List[models.NotebookType]) -> None:
        """Show list of notebook types or message if no types found."""
        if types and len(types) > 0:
            print('All notebook types:')
            for t in types:
                print(f'  {t.title}  {t.page_width}x{t.page_height}mm')
        else:
            print('No types found.')
