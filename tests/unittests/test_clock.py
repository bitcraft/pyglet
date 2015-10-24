import unittest
import mock
import pyglet.clock


class ClockTestCase(unittest.TestCase):
    """Test clock using dummy time keeper

    not tested:
      positional and named arguments
    """

    def setUp(self):
        self.interval = .001
        self.time = 0
        self.callback_a = mock.Mock()
        self.callback_b = mock.Mock()
        self.callback_c = mock.Mock()
        self.callback_d = mock.Mock()
        self.clock = pyglet.clock.Clock(time_function=lambda: self.time)

    def advance_clock(self, dt=1):
        """simulate the passage of time like a real clock would"""
        frames = 0
        end = self.time + dt
        while self.time < end:
            frames += 1
            self.time += self.interval
            self.clock.tick()
        self.time = round(self.time, 0)
        return frames

    def test_schedule(self):
        self.clock.schedule(self.callback_a)
        frames = self.advance_clock()
        self.assertEqual(self.callback_a.call_count, frames)

    def test_schedule_once(self):
        self.clock.schedule_once(self.callback_a, 1)
        self.advance_clock(2)
        self.assertEqual(self.callback_a.call_count, 1)

    def test_schedule_once_multiple(self):
        self.clock.schedule_once(self.callback_a, 1)
        self.clock.schedule_once(self.callback_b, 2)
        self.advance_clock(2)
        self.assertEqual(self.callback_a.call_count, 1)
        self.assertEqual(self.callback_b.call_count, 1)

    def test_schedule_interval(self):
        self.clock.schedule_interval(self.callback_a, 1)
        self.advance_clock(2)
        self.assertEqual(self.callback_a.call_count, 2)

    def test_schedule_interval_multiple(self):
        self.clock.schedule_interval(self.callback_a, 1)
        self.clock.schedule_interval(self.callback_b, 1)
        self.advance_clock(2)
        self.assertEqual(self.callback_a.call_count, 2)
        self.assertEqual(self.callback_b.call_count, 2)

    def test_schedule_interval_soft(self):
        self.clock.schedule_interval_soft(self.callback_a, 1)
        self.advance_clock(2)
        self.assertEqual(self.callback_a.call_count, 2)

    def test_schedule_interval_soft_multiple(self):
        self.clock.schedule_interval(self.callback_a, 1)
        self.clock.schedule_interval_soft(self.callback_b, 1)
        self.clock.schedule_interval_soft(self.callback_b, 1)
        next_ts = set(i.next_ts for i in self.clock._scheduled_items)
        self.assertEqual(len(next_ts), 3)
        self.advance_clock()
        self.assertEqual(self.callback_a.call_count, 1)
        self.assertEqual(self.callback_b.call_count, 2)

    def test_schedule_unschedule(self):
        self.clock.schedule(self.callback_a)
        self.clock.unschedule(self.callback_a)
        self.advance_clock()
        self.assertEqual(self.callback_a.call_count, 0)

    def test_schedule_once_unschedule(self):
        self.clock.schedule_once(self.callback_a, 1)
        self.clock.unschedule(self.callback_a)
        self.advance_clock()
        self.assertEqual(self.callback_a.call_count, 0)

        # relies on access to private member
        self.assertEqual(len(self.clock._every_tick_items), 0)

    def test_schedule_interval_unschedule(self):
        self.clock.schedule_interval(self.callback_a, 1)
        self.clock.unschedule(self.callback_a)
        self.advance_clock()
        self.assertEqual(self.callback_a.call_count, 0)

        # relies on access to private member
        self.assertEqual(len(self.clock._scheduled_items), 0)

    def test_schedule_interval_soft_unschedule(self):
        self.clock.schedule_interval_soft(self.callback_a, 1)
        self.clock.unschedule(self.callback_a)
        self.advance_clock()
        self.assertEqual(self.callback_a.call_count, 0)

        # relies on access to private member
        self.assertEqual(len(self.clock._scheduled_items), 0)

    def test_unschedule_removes_all(self):
        self.clock.schedule(self.callback_a)
        self.clock.schedule_once(self.callback_a, 1)
        self.clock.schedule_interval(self.callback_a, 1)
        self.clock.schedule_interval_soft(self.callback_a, 1)
        self.clock.schedule(self.callback_a)
        self.clock.schedule(self.callback_b)
        self.clock.unschedule(self.callback_a)
        frames = self.advance_clock(10)
        self.assertEqual(self.callback_a.call_count, 0)
        self.assertEqual(self.callback_b.call_count, frames)

        # relies on access to private member
        self.assertEqual(len(self.clock._every_tick_items), 1)
        self.assertEqual(len(self.clock._scheduled_items), 0)
        self.assertEqual(self.clock._every_tick_items[0].func, self.callback_b)

    def test_schedule_will_not_call_function(self):
        self.clock.schedule(self.callback_a)
        self.assertEqual(self.callback_a.call_count, 0)
        self.clock.schedule_once(self.callback_a, 0)
        self.assertEqual(self.callback_a.call_count, 0)
        self.clock.schedule_interval(self.callback_a, 1)
        self.assertEqual(self.callback_a.call_count, 0)
        self.clock.schedule_interval_soft(self.callback_a, 1)
        self.assertEqual(self.callback_a.call_count, 0)

    def test_unschedule_will_not_call_function(self):
        self.clock.schedule(self.callback_a)
        self.clock.unschedule(self.callback_a)
        self.assertEqual(self.callback_a.call_count, 0)
        self.clock.schedule_once(self.callback_a, 0)
        self.clock.unschedule(self.callback_a)
        self.assertEqual(self.callback_a.call_count, 0)
        self.clock.schedule_interval(self.callback_a, 1)
        self.clock.unschedule(self.callback_a)
        self.assertEqual(self.callback_a.call_count, 0)
        self.clock.schedule_interval_soft(self.callback_a, 1)
        self.clock.unschedule(self.callback_a)
        self.assertEqual(self.callback_a.call_count, 0)

    def test_unschedule_will_not_fail_if_already_unscheduled(self):
        self.clock.schedule(self.callback_a)
        self.clock.unschedule(self.callback_a)
        self.clock.unschedule(self.callback_a)
        self.clock.schedule_once(self.callback_a, 0)
        self.clock.unschedule(self.callback_a)
        self.clock.unschedule(self.callback_a)
        self.clock.schedule_interval(self.callback_a, 1)
        self.clock.unschedule(self.callback_a)
        self.clock.unschedule(self.callback_a)
        self.clock.schedule_interval_soft(self.callback_a, 1)
        self.clock.unschedule(self.callback_a)
        self.clock.unschedule(self.callback_a)

    def test_call_sched_return_True_if_called_functions(self):
        self.clock.schedule(self.callback_a)
        self.assertTrue(self.clock.call_scheduled_functions(0))

    def test_call_sched_return_True_if_called_functions_interval(self):
        self.clock.schedule_once(self.callback_a, 1)
        self.assertFalse(self.clock.call_scheduled_functions(0))
        self.clock.set_time(1)
        self.assertTrue(self.clock.call_scheduled_functions(0))

    def test_call_sched_return_False_if_no_called_functions(self):
        self.assertFalse(self.clock.call_scheduled_functions(0))

    def test_tick_return_last_delta(self):
        self.assertEqual(self.clock.tick(), 0)
        self.time = 1
        self.assertEqual(self.clock.tick(), 1)
        self.time = 3
        self.assertEqual(self.clock.tick(), 2)

    def test_get_sleep_time_None_if_no_items(self):
        self.assertIsNone(self.clock.get_sleep_time())

    def test_get_sleep_time_can_sleep(self):
        self.clock.schedule_once(self.callback_a, 3)
        self.clock.schedule_once(self.callback_b, 1)
        self.clock.schedule_once(self.callback_c, 6)
        self.clock.schedule_once(self.callback_d, 7)
        self.assertEqual(self.clock.get_sleep_time(), 1)
        self.advance_clock()
        self.assertEqual(self.clock.get_sleep_time(), 2)
        self.advance_clock(2)
        self.assertEqual(self.clock.get_sleep_time(), 3)
        self.advance_clock(3)
        self.assertEqual(self.clock.get_sleep_time(), 1)

    def test_get_sleep_time_cannot_sleep(self):
        self.clock.schedule(self.callback_a)
        self.clock.schedule_once(self.callback_b, 1)
        self.assertEqual(self.clock.get_sleep_time(), 0)

    def test_unschedule_item_during_tick(self):
        def suicidal_event(dt):
            sock()
            self.clock.unschedule(suicidal_event)

        sock = mock.Mock()
        self.clock.schedule(suicidal_event)
        self.advance_clock()
        self.assertEqual(sock.call_count, 1)

    def test_schedule_item_during_tick(self):
        def replicating_event(dt):
            self.clock.schedule(replicating_event)
            sock()

        sock = mock.Mock()
        self.clock.schedule(replicating_event)

        # one tick for the original event
        self.clock.tick()
        self.assertEqual(sock.call_count, 1)

        # requires access to private member
        self.assertEqual(len(self.clock._every_tick_items), 2)

        # one tick from original, then two for new
        # now event queue should have two items as well
        self.clock.tick()
        self.assertEqual(sock.call_count, 3)

        # requires access to private member
        self.assertEqual(len(self.clock._every_tick_items), 4)

    def test_unschedule_interval_item_during_tick(self):
        def suicidal_event(dt):
            sock()
            self.clock.unschedule(suicidal_event)

        sock = mock.Mock()
        self.clock.schedule_interval(suicidal_event, 1)
        self.advance_clock()
        self.assertEqual(sock.call_count, 1)

    def test_schedule_interval_item_during_tick(self):
        def replicating_event(dt):
            self.clock.schedule_interval(replicating_event, 1)
            sock()

        sock = mock.Mock()
        self.clock.schedule_interval(replicating_event, 1)

        # one tick for the original event
        self.advance_clock()
        self.assertEqual(sock.call_count, 1)

        # requires access to private member
        self.assertEqual(len(self.clock._scheduled_items), 2)

        # one tick from original, then two for new
        # now event queue should have two items as well
        self.advance_clock()
        self.assertEqual(sock.call_count, 3)

        # requires access to private member
        self.assertEqual(len(self.clock._scheduled_items), 4)

    def test_slow_clock_doesnt_repeat_calls(self):
        """pyglet's clock will not make up for lost time.  in this case, the
        interval scheduled for callback_[bcd] is 1, and 2 seconds have passed.
        since pyglet won't make up for lost time, they are only called once.
        """
        self.clock.schedule(self.callback_a)
        self.clock.schedule_once(self.callback_b, 1)
        self.clock.schedule_interval(self.callback_c, 1)
        self.clock.schedule_interval_soft(self.callback_d, 1)

        # simulate slow clock
        self.time = 2
        self.clock.tick()

        self.assertEqual(self.callback_a.call_count, 1)
        self.assertEqual(self.callback_b.call_count, 1)
        self.assertEqual(self.callback_c.call_count, 1)
        self.assertEqual(self.callback_d.call_count, 1)

    def test_slow_clock_reschedules(self):
        """pyglet's clock will not make up for lost time.  in this case, the
        interval scheduled for callback_[bcd] is 1, and 2 seconds have passed.
        since pyglet won't make up for lost time, they are only called once.
        this test verifies that missed events are rescheduled and executed later
        """
        self.clock.schedule(self.callback_a)
        self.clock.schedule_once(self.callback_b, 1)
        self.clock.schedule_interval(self.callback_c, 1)
        self.clock.schedule_interval_soft(self.callback_d, 1)

        # simulate slow clock
        self.time = 2
        self.clock.tick()

        # simulate a proper clock
        frames = self.advance_clock()

        # make sure our clock is at 3 seconds
        self.assertEqual(self.time, 3)

        # the +1 is the call during the slow clock period
        self.assertEqual(self.callback_a.call_count, frames + 1)

        # only scheduled to happen once
        self.assertEqual(self.callback_b.call_count, 1)

        # 2 because they 'missed' a call when the clock lagged
        # with a good clock, this would be 3
        self.assertEqual(self.callback_c.call_count, 2)
        self.assertEqual(self.callback_d.call_count, 2)

    def test_get_interval(self):
        self.assertEqual(self.clock.get_interval(), 0)
        self.advance_clock(100)
        self.assertEqual(round(self.clock.get_interval(), 10), self.interval)

    def test_soft_scheduling_stress_test(self):
        """test that the soft scheduler is able to correctly soft-schedule
        several overlapping events.
        this test delves into implementation of the clock, and may break
        """
        # this value represents evenly scheduled items between 0 & 1
        # and what is produced by the correct soft-scheduler
        expected = [0.0625, 0.125, 0.1875, 0.25, 0.3125, 0.375, 0.4375, 0.5,
                    0.5625, 0.625, 0.6875, 0.75, 0.8125, 0.875, 0.9375, 1]

        for i in range(16):
            self.clock.schedule_interval_soft(None, 1)

        # sort the clock items
        items = sorted(i.next_ts for i in self.clock._scheduled_items)

        self.assertEqual(items, expected)
