"""Test that window can be resized.

Expected behaviour:
    One window will be opened.  It should be resizable by the user.

    Close the window or press ESC to end the test.
"""


import unittest

from pyglet.gl import *
from pyglet import window

from tests.interactive.window import window_util


class WindowResizable(unittest.TestCase):

    def test_resizable(self):
        print(__doc__)
        self.width, self.height = 200, 200
        self.w = w = window.Window(self.width, self.height, resizable=True)
        glClearColor(1, 1, 1, 1)
        while not w.has_exit:
            w.dispatch_events()
            window_util.draw_client_border(w)
            w.flip()
        w.close()
