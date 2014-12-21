"""Test that audio playback works.

You may want to turn down the volume of your speakers.
"""

import unittest

from pyglet import media
from pyglet.media import procedural
import time


class PlayerInteractiveTests(unittest.TestCase):
    def test_eos_next(self):
        """You should hear a tone at 440Hz (A above middle C) for 1.0 seconds.
           The test will exit immediately after.
        """
        source1 = procedural.Sine(0.5)
        source2 = procedural.Sine(0.5)
        player = media.Player()
        player.queue(source1)
        player.queue(source2)
        player.play()

    def test_static_static(self):
        """You should hear white noise (static) for 0.5 seconds.
           The test will exit immediately after.
        """
        source = procedural.WhiteNoise(0.5)
        source = media.StaticSource(source)
        source = media.StaticSource(source)
        player = media.Player()
        player.queue(source)
        player.play()

    def test_queue_play(self):
        """You should hear white noise (static) for 0.5 seconds.
           The test will exit immediately after.
        """
        source = procedural.WhiteNoise(0.5)
        player = media.Player()
        player.queue(source)
        player.play()

    def test_play_queue(self):
        """You should hear white noise (static) for 0.5 seconds.
           The test will exit immediately after.
        """
        source = procedural.WhiteNoise(0.5)
        player = media.Player()
        player.play()
        player.queue(source)

    def test_pause_queue(self):
        """You should hear white noise (static) for 0.5 seconds.
           The test will exit immediately after.
        """
        source = procedural.WhiteNoise(0.5)
        player = media.Player()
        player.pause()
        player.queue(source)

        while player.source:
            player.dispatch_events()
            player.play()

    def test_pause(self):
        """You should hear white noise (static) for 0.25 seconds, then a 0.5
           second pause then another 0.25 seconds of noise.  The test will exit
           immediately after.
        """
        source = procedural.WhiteNoise(0.5)
        player = media.Player()
        player.queue(source)
        player.play()
        start_time = time.time()

        stage = 0
        while player.source:
            if stage == 0 and time.time() - start_time > 0.25:
                player.pause()
                stage = 1
            if stage == 1 and time.time() - start_time > 0.75:
                player.play()
                stage = 2
            player.dispatch_events()
