"""Test that mouse drag event works correctly.

Expected behaviour:
    One window will be opened.  Click and drag with the mouse and ensure
    that buttons, coordinates and modifiers are reported correctly.  Events
    should be generated even when the drag leaves the window.

    Close the window or press ESC to end the test.
"""


import unittest

from pyglet import window


class EventMouseDrag(unittest.TestCase):

    def test_mouse_drag(self):
        w = window.Window(200, 200)
        while not w.has_exit:
            w.dispatch_events()
        w.close()
