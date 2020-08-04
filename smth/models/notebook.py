# License: GNU GPL Version 3

"""The module provides the Notebook model."""

import math
import pathlib

from PIL import Image as pillow

from smth import const

from .notebook_type import NotebookType


class Notebook:  # pylint: disable=too-many-instance-attributes
    """Collection of pages orderded by their numbers."""

    def __init__(
            self, title: str, notebook_type: NotebookType, path: pathlib.Path):
        self.id = -1
        self.title = title
        self._type = notebook_type
        self.path = path
        self.total_pages = 0
        self.first_page_number = 1

    @property
    def id(self) -> int:  # pylint: disable=invalid-name
        """Notebook's id in the database."""
        return self._id

    @id.setter
    def id(self, id_) -> None:  # pylint: disable=invalid-name
        self._id = id_

    @property
    def title(self) -> str:
        """Title of the notebook. Must be unique."""
        return self._title

    @title.setter
    def title(self, title: str) -> None:
        self._title = title if title else 'Untitled'

    @property
    def type(self) -> NotebookType:
        """Type of the notebook (page size, etc.)."""
        return self._type

    @property
    def path(self) -> pathlib.Path:
        """Path to PDF file in the filesystem."""
        return self._path

    @path.setter
    def path(self, path: pathlib.Path) -> None:
        self._path = path

    @property
    def total_pages(self) -> int:
        """Number of pages in the notebook."""
        return self._total_pages

    @total_pages.setter
    def total_pages(self, total_pages) -> None:
        if total_pages >= 0:
            self._total_pages = total_pages
        else:
            total_pages = 0

    @property
    def first_page_number(self) -> int:
        """A number from which page numbering should start."""
        return self._first_page_number

    @first_page_number.setter
    def first_page_number(self, number) -> None:
        if number >= 0:
            self._first_page_number = number
        else:
            self._first_page_number = 1

    def crop_image(  # pylint: disable=too-many-branches
            self, page: int, image: pillow.Image,
            resolution: int) -> pillow.Image:
        """Rotate and crop image so it fits the notebook's type."""
        img = image.copy()

        orig_width, orig_height = img.size

        if orig_width > orig_height:
            img = img.rotate(90, expand=True)
            orig_width, orig_height = img.size

        page_width_pt = math.ceil(self.type.page_width * resolution / 25.4)
        page_height_pt = math.ceil(self.type.page_height * resolution / 25.4)

        if self.type.pages_paired:
            if page_height_pt < orig_width:
                img = img.rotate(-90, expand=True)
                orig_width, orig_height = img.size

            if self.first_page_number % 2 == page % 2:
                # left page, crop from left side
                if page_width_pt < orig_width:
                    img = img.crop((0, 0, page_width_pt, orig_height))
            else:
                # right page, crop from right side
                if page_width_pt < orig_width:
                    if page_width_pt * 2 < orig_width:
                        offset_x = page_width_pt
                    else:
                        offset_x = orig_width - page_width_pt

                    box = (offset_x, 0, page_width_pt + offset_x, orig_height)
                    img = img.crop(box)

            if page_height_pt < orig_height:
                img = img.crop((0, 0, img.size[0], page_height_pt))
        else:
            if page_width_pt > page_height_pt:
                img = img.rotate(-90, expand=True)
                orig_width, orig_height = img.size

            if page_width_pt < orig_width:
                img = img.crop((0, 0, page_width_pt, orig_height))

            if page_height_pt < orig_height:
                img = img.crop((0, 0, img.size[0], page_height_pt))

        return img

    def get_page_path(self, page: int) -> pathlib.Path:
        """Return absolute path to notebook's page with given number."""
        return const.PAGES_ROOT_PATH / self.title / f'{page}.jpg'

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                other.title == self.title)

    def __repr__(self):
        return f"<Notebook '{self._title}' of type '{self._type.title}'>"
