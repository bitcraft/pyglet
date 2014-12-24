"""Test that window style can be dialog.

Expected behaviour:
    One dialog-styled window will be opened.

    Close the window or press ESC to end the test.
"""


import unittest

from pyglet.gl import *
from pyglet import window
from pyglet.window import key


class TEST_WINDOW_STYLE_DIALOG(unittest.TestCase):

    def test_style_dialog(self):
        print(__doc__)
        self.width, self.height = 200, 200
        self.w = w = window.Window(self.width, self.height,
                                   style=window.Window.WINDOW_STYLE_DIALOG)
        glClearColor(1, 1, 1, 1)
        while not w.has_exit:
            glClear(GL_COLOR_BUFFER_BIT)
            w.dispatch_events()
            w.flip()
        w.close()
