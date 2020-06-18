import math
import unittest
from typing import Tuple

from PIL import Image

from smth import models


class CropImageTestCase(unittest.TestCase):
    """Tests on image cropping after scanning."""

    def setUp(self):
        self.type = models.NotebookType('', 100, 200)
        self.notebook = models.Notebook('', self.type, '')
        self.resolution = 150

    def test_crop_portrait_single_page(self):
        orig_image = self._new_image(220, 300)
        self._set_type_size_mm(210, 297)
        image = self.notebook.crop_image(1, orig_image, self.resolution)
        self.assertTupleEqual(image.size, self._type_size_pt())

    def test_crop_portrait_single_page_too_wide(self):
        orig_image = self._new_image(220, 300)
        self._set_type_size_mm(240, 297)
        image = self.notebook.crop_image(1, orig_image, self.resolution)
        expected = (orig_image.size[0], self._type_height_pt())
        self.assertTupleEqual(image.size, expected)

    def test_crop_portrait_single_page_too_long(self):
        orig_image = self._new_image(220, 300)
        self._set_type_size_mm(210, 320)
        image = self.notebook.crop_image(1, orig_image, self.resolution)
        expected = (self._type_width_pt(), orig_image.size[1])
        self.assertTupleEqual(image.size, expected)

    def test_crop_portrait_single_page_too_large(self):
        orig_image = self._new_image(220, 300)
        self._set_type_size_mm(240, 320)
        image = self.notebook.crop_image(1, orig_image, self.resolution)
        self.assertTupleEqual(image.size, orig_image.size)

    def test_crop_landscape_single_page(self):
        orig_image = self._new_image(220, 300)
        self._set_type_size_mm(297, 210)
        image = self.notebook.crop_image(1, orig_image, self.resolution)
        self.assertTupleEqual(image.size, self._type_size_pt())

    def test_crop_landscape_single_page_too_wide(self):
        orig_image = self._new_image(220, 300)
        self._set_type_size_mm(320, 210)
        image = self.notebook.crop_image(1, orig_image, self.resolution)
        expected = (orig_image.size[1], self._type_height_pt())
        self.assertTupleEqual(image.size, expected)

    def test_crop_landscape_single_page_too_long(self):
        orig_image = self._new_image(220, 300)
        self._set_type_size_mm(297, 240)
        image = self.notebook.crop_image(1, orig_image, self.resolution)
        expected = (self._type_width_pt(), orig_image.size[0])
        self.assertTupleEqual(image.size, expected)

    def test_crop_landscape_single_page_too_large(self):
        orig_image = self._new_image(220, 300)
        self._set_type_size_mm(320, 240)
        image = self.notebook.crop_image(1, orig_image, self.resolution)
        expected = (orig_image.size[1], orig_image.size[0])
        self.assertTupleEqual(image.size, expected)

    def test_crop_paired_pages_left_page(self):
        orig_image = self._new_image(220, 300)
        self._set_type_size_mm(170, 200)
        self.notebook.type.pages_paired = True
        image = self.notebook.crop_image(1, orig_image, self.resolution)
        self.assertTupleEqual(image.size, self._type_size_pt())

    def test_crop_paired_pages_right_page(self):
        orig_image = self._new_image(220, 300)
        self._set_type_size_mm(170, 200)
        self.notebook.type.pages_paired = True
        image = self.notebook.crop_image(2, orig_image, self.resolution)
        self.assertTupleEqual(image.size, self._type_size_pt())

    def test_crop_paired_pages_left_page_portrait_only(self):
        orig_image = self._new_image(220, 300)
        self._set_type_size_mm(210, 297)
        self.notebook.type.pages_paired = True
        image = self.notebook.crop_image(1, orig_image, self.resolution)
        self.assertTupleEqual(image.size, self._type_size_pt())

    def test_crop_paired_pages_right_page_protrait_only(self):
        orig_image = self._new_image(220, 300)
        self._set_type_size_mm(210, 297)
        self.notebook.type.pages_paired = True
        image = self.notebook.crop_image(2, orig_image, self.resolution)
        self.assertTupleEqual(image.size, self._type_size_pt())

    def test_crop_paired_pages_two_pages_at_once_left_page(self):
        orig_image = self._new_image(220, 300)
        self._set_type_size_mm(100, 150)
        self.notebook.type.pages_paired = True
        image = self.notebook.crop_image(1, orig_image, self.resolution)
        self.assertTupleEqual(image.size, self._type_size_pt())

    def test_crop_paired_pages_two_pages_at_once_right_page(self):
        orig_image = self._new_image(220, 300)
        self._set_type_size_mm(100, 150)
        self.notebook.type.pages_paired = True
        image = self.notebook.crop_image(2, orig_image, self.resolution)
        self.assertTupleEqual(image.size, self._type_size_pt())

    def test_crop_orig_landscape(self):
        orig_image = self._new_image(300, 220)
        self._set_type_size_mm(100, 150)
        image = self.notebook.crop_image(1, orig_image, self.resolution)
        self.assertTupleEqual(image.size, self._type_size_pt())

    def _new_image(self, width_mm: int, height_mm: int) -> Image.Image:
        return Image.new(
            'RGB', (self._mm_to_pt(width_mm), self._mm_to_pt(height_mm)))

    def _set_type_size_mm(self, width_mm: int, height_mm: int) -> None:
        self.type.page_width = width_mm
        self.type.page_height = height_mm

    def _type_width_pt(self) -> int:
        return self._mm_to_pt(self.type.page_width)

    def _type_height_pt(self) -> int:
        return self._mm_to_pt(self.type.page_height)

    def _type_size_pt(self) -> Tuple[int]:
        return self._type_width_pt(), self._type_height_pt()

    def _mm_to_pt(self, size_mm: int) -> int:
        return math.ceil(size_mm * self.resolution / 25.4)
