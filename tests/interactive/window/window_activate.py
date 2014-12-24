"""Test that the window can be activated (focus set).

Expected behaviour:
    One window will be opened.  Every 5 seconds it will be activated;
    it should be come to the front and accept keyboard input (this will
    be shown on the terminal).

    On Windows XP, the taskbar icon may flash (indicating the application
    requires attention) rather than moving the window to the foreground.  This
    is the correct behaviour.

    Press escape or close the window to finished the test.
"""


import time
import unittest

from pyglet import window


class WindowActivate(unittest.TestCase):

    def test_activate(self):
        print(__doc__)
        w = window.Window(200, 200)
        last_time = time.time()
        while not w.has_exit:
            if time.time() - last_time > 5:
                w.activate()
                last_time = time.time()
                print('Activated window.')
            w.dispatch_events()
        w.close()
