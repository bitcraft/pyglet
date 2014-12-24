"""Press a letter to switch to the corresponding mode"""

import unittest

from pyglet import window
from pyglet.gl import *

from tests.interactive.window import window_util


class WINDOW_SET_FULLSCREEN(unittest.TestCase):

    def on_text(self, text):
        text = text[:1]
        i = ord(text) - ord('a')
        if 0 <= i < len(self.modes):
            print('Switching to %s' % self.modes[i])
            self.w.screen.set_mode(self.modes[i])

    def on_expose(self):
        glClearColor(1, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        window_util.draw_client_border(self.w)
        self.w.flip()

    def test_set_fullscreen(self):
        print(__doc__)
        self.w = w = window.Window(200, 200)
        self.modes = w.screen.get_modes()
        for i, mode in enumerate(self.modes):
            print('%s: %s' % (chr(i + ord('a')), mode))

        w.push_handlers(self)
        self.on_expose()
        while not w.has_exit:
            w.dispatch_events()
        w.close()
