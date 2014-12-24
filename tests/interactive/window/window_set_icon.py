"""Test that window icon can be set.

Expected behaviour:
    One window will be opened.  It will have an icon depicting a yellow
    "A".

    Close the window or press ESC to end the test.
"""


import unittest

from pyglet.gl import *
from pyglet import image
from pyglet import window
from pyglet.window import key

from os.path import join, dirname

icon_file = join(dirname(__file__), 'icon1.png')


class WINDOW_SET_ICON(unittest.TestCase):

    def test_set_icon(self):
        print(__doc__)
        self.width, self.height = 200, 200
        self.w = w = window.Window(self.width, self.height)
        w.set_icon(image.load(icon_file))
        glClearColor(1, 1, 1, 1)
        while not w.has_exit:
            glClear(GL_COLOR_BUFFER_BIT)
            w.dispatch_events()
            w.flip()
        w.close()
