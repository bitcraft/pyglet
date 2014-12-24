"""Test that a font with no name given still renders using some sort
of default system font.
"""


import unittest

from . import base_text


class TEST_DEFAULT(base_text.TextTestBase):
    font_name = ''
