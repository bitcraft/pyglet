"""Test that font colour is applied correctly.   Default font should
appear at 0.1 opacity (faint white)
"""


import unittest
from . import base_text

from pyglet import font


class TEST_COLOR_BLEND(base_text.TextTestBase):

    def render(self):
        fnt = font.load(self.font_name, self.font_size)
        self.label = font.Text(fnt, self.text, 10, 10, color=(1, 1, 1, 0.1))
