"""Test that a scheduled function gets called every interval with the correct
time delta.
"""

import time
import unittest

from pyglet import clock

__noninteractive = True


class Multicore(unittest.TestCase):

    def test_multicore(self):
        failures = 0
        old_time = time.clock()
        end_time = time.time() + 3
        while time.time() < end_time:
            t = time.clock()
            if t < old_time:
                failures += 1
            old_time = t
            time.sleep(0.001)
        self.assertEqual(failures, 0)


class Schedule(unittest.TestCase):
    callback_dt = None
    callback_count = 0

    def callback(self, dt):
        self.callback_dt = dt
        self.callback_count += 1

    def test_schedule(self):
        clock.set_default(clock.Clock())
        clock.schedule(self.callback)

        result = clock.tick()
        self.assertEqual(result, self.callback_dt)
        self.callback_dt = None
        time.sleep(1)

        result = clock.tick()
        self.assertEqual(result, self.callback_dt)
        self.callback_dt = None
        time.sleep(1)

        result = clock.tick()
        self.assertEqual(result, self.callback_dt)

    def test_unschedule(self):
        clock.set_default(clock.Clock())
        clock.schedule(self.callback)

        result = clock.tick()
        self.assertEqual(result, self.callback_dt)
        self.callback_dt = None
        time.sleep(1)
        clock.unschedule(self.callback)

        result = clock.tick()
        self.assertIsNone(self.callback_dt)

    def test_schedule_multiple(self):
        clock.set_default(clock.Clock())
        clock.schedule(self.callback)
        clock.schedule(self.callback)
        self.callback_count = 0

        clock.tick()
        self.assertEqual(self.callback_count, 2)
        clock.unschedule(self.callback)

        clock.tick()
        self.assertEqual(self.callback_count, 2)


class ScheduleInterval(unittest.TestCase):
    callback_1_count = 0
    callback_2_count = 0
    callback_3_count = 0

    def callback_1(self, dt):
        self.assertTrue(abs(dt - 0.1) < 0.06)
        self.callback_1_count += 1

    def callback_2(self, dt):
        self.assertTrue(abs(dt - 0.35) < 0.06)
        self.callback_2_count += 1

    def callback_3(self, dt):
        self.assertTrue(abs(dt - 0.07) < 0.06)
        self.callback_3_count += 1

    def clear(self):
        self.callback_1_count = 0
        self.callback_2_count = 0
        self.callback_3_count = 0

    def test_schedule_interval(self):
        self.clear()
        clock.set_default(clock.Clock())
        clock.schedule_interval(self.callback_1, 0.1)
        clock.schedule_interval(self.callback_2, 0.35)
        clock.schedule_interval(self.callback_3, 0.07)

        t = 0
        while t < 2.04:  # number chosen to avoid +/- 1 errors in div
            t += clock.tick()
        self.assertTrue(self.callback_1_count == int(t / 0.1))
        self.assertTrue(self.callback_2_count == int(t / 0.35))
        self.assertTrue(self.callback_3_count == int(t / 0.07))


class ScheduleOnce(unittest.TestCase):
    callback_1_count = 0
    callback_2_count = 0
    callback_3_count = 0

    def callback_1(self, dt):
        self.assertLess(abs(dt - 0.1), 0.01)
        self.callback_1_count += 1

    def callback_2(self, dt):
        self.assertLess(abs(dt - 0.35), 0.01)
        self.callback_2_count += 1

    def callback_3(self, dt):
        self.assertLess(abs(dt - 0.07), 0.01)
        self.callback_3_count += 1

    def clear(self):
        self.callback_1_count = 0
        self.callback_2_count = 0
        self.callback_3_count = 0

    def test_schedule_once(self):
        self.clear()
        clock.set_default(clock.Clock())
        clock.schedule_once(self.callback_1, 0.1)
        clock.schedule_once(self.callback_2, 0.35)
        clock.schedule_once(self.callback_3, 0.07)

        t = 0
        while t < 1:
            t += clock.tick()
        self.assertEqual(self.callback_1_count, 1)
        self.assertEqual(self.callback_2_count, 1)
        self.assertEqual(self.callback_3_count, 1)
