# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

"""Precise framerate calculation, scheduling and framerate limiting.

Scheduling
==========

You can schedule a function to be called every time the clock is ticked::

    def callback(dt):
        print '%f seconds since last callback' % dt

    clock.schedule(callback)

The `schedule_interval` method causes a function to be called every "n"
seconds::

    clock.schedule_interval(callback, .5)   # called twice a second

The `schedule_once` method causes a function to be called once "n" seconds
in the future::

    clock.schedule_once(callback, 5)        # called in 5 seconds

All of the `schedule` methods will pass on any additional args or keyword args
you specify to the callback function::

    def animate(dt, velocity, sprite):
       sprite.position += dt * velocity

    clock.schedule(animate, velocity=5.0, sprite=alien)

You can cancel a function scheduled with any of these methods using
`unschedule`::

    clock.unschedule(animate)

Displaying FPS
==============

The ClockDisplay class provides a simple FPS counter.  You should create
an instance of ClockDisplay once during the application's start up::

    fps_display = clock.ClockDisplay()

Call draw on the ClockDisplay object for each frame::

    fps_display.draw()

There are several options to change the font, color and text displayed
within the __init__ method.

Using multiple clocks
=====================

The clock functions are all relayed to an instance of `Clock` which is
initialised with the module.  You can get this instance to use directly::

    clk = clock.get_default()

You can also replace the default clock with your own:

    myclk = clock.Clock()
    clock.set_default(myclk)

Each clock maintains its own set of scheduled functions and FPS
limiting/measurement.  Each clock must be "ticked" separately.

Multiple and derived clocks potentially allow you to separate "game-time" and
"wall-time", or to synchronise your clock to an audio or video stream instead
of the system clock.
"""

__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import time
import ctypes

import pyglet.lib
from pyglet import compat_platform

if compat_platform in ('win32', 'cygwin'):
    # Win32 Sleep function is only 10-millisecond resolution, so instead
    # use a waitable timer object, which has up to 100-nanosecond resolution
    # (hardware and implementation dependent, of course).
    kernel32 = ctypes.windll.kernel32

    class _ClockBase:

        def __init__(self):
            self._timer = kernel32.CreateWaitableTimerA(None, True, None)

        def sleep(self, microseconds):
            delay = ctypes.c_longlong(int(-microseconds * 10))
            kernel32.SetWaitableTimer(self._timer, ctypes.byref(delay),
                                       0, ctypes.c_void_p(), ctypes.c_void_p(),
                                       False)
            kernel32.WaitForSingleObject(self._timer, 0xffffffff)

    _default_time_function = time.perf_counter

else:
    _c = pyglet.lib.load_library('c')
    _c.usleep.argtypes = [ctypes.c_ulong]

    class _ClockBase:

        def sleep(self, microseconds):
            _c.usleep(int(microseconds))

    _default_time_function = time.perf_counter


class _ScheduledItem:
    __slots__ = ['func', 'args', 'kwargs']

    def __init__(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs


class _ScheduledIntervalItem:
    __slots__ = ['func', 'interval', 'last_ts', 'next_ts', 'args', 'kwargs']

    def __init__(self, func, interval, last_ts, next_ts, args, kwargs):
        self.func = func
        self.interval = interval
        self.last_ts = last_ts
        self.next_ts = next_ts
        self.args = args
        self.kwargs = kwargs


def _dummy_schedule_func(*args, **kwargs):
    """Dummy function that does nothing, placed onto zombie scheduled items
    to ensure they have no side effect if already queued.
    """
    pass


class Clock(_ClockBase):

    """Class for scheduling functions.
    """

    def __init__(self, time_function=_default_time_function):
        """Initialise a Clock, with optional custom time function.

        :Parameters:
            `time_function` : function
                Function to return the elapsed time of the application,
                in seconds.  Defaults to time.time, but can be replaced
                to allow for easy time dilation effects or game pausing.

        """
        super().__init__()
        self.time = time_function
        self.next_ts = self.time()
        self.last_ts = None
        self.times = list()
        self.cumulative_time = 0
        self.window_size = 0

        self._schedule_items = list()
        self._schedule_interval_items = list()

    def update_time(self):
        """Get the elapsed time since the last call to `update_time`.

        This updates the clock's internal measure of time and returns
        the difference since the last update (or since the clock was created).

        :since: pyglet 1.2

        :rtype: float
        :return: The number of seconds since the last `update_time`, or 0
                 if this was the first time it was called.
        """
        ts = self.time()
        if self.last_ts is None:
            delta_t = 0
        else:
            delta_t = ts - self.last_ts
            self.times.insert(0, delta_t)
            if len(self.times) > self.window_size:
                self.cumulative_time -= self.times.pop()
        self.cumulative_time += delta_t
        self.last_ts = ts

        return delta_t

    def call_scheduled_functions(self, dt):
        """Call scheduled functions that elapsed on the last `update_time`.

        :since: pyglet 1.2

        :Parameters:
            dt : float
                The elapsed time since the last update to pass to each
                scheduled function.  This is *not* used to calculate which
                functions have elapsed.

        :rtype: bool
        :return: True if any functions were called, otherwise False.
        """
        ts = self.last_ts
        result = False

        # Call functions scheduled for every frame
        # Dupe list just in case one of the items unchedules itself
        for item in list(self._schedule_items):
            result = True
            item.func(dt, *item.args, **item.kwargs)

        # Call all scheduled interval functions and reschedule for future.
        need_resort = False
        # Dupe list just in case one of the items unchedules itself
        for item in list(self._schedule_interval_items):
            if item.next_ts > ts:
                break
            result = True
            item.func(ts - item.last_ts, *item.args, **item.kwargs)
            if item.interval:
                # Try to keep timing regular, even if overslept this time;
                # but don't schedule in the past (which could lead to
                # infinitely-worsing error).
                item.next_ts = item.last_ts + item.interval
                item.last_ts = ts
                if item.next_ts <= ts:
                    if ts - item.next_ts < 0.05:
                        # Only missed by a little bit, keep the same schedule
                        item.next_ts = ts + item.interval
                    else:
                        # Missed by heaps, do a soft reschedule to avoid
                        # lumping everything together.
                        item.next_ts = self._get_soft_next_ts(
                            ts, item.interval)
                        # Fake last_ts to avoid repeatedly over-scheduling in
                        # future.  Unfortunately means the next reported dt is
                        # incorrect (looks like interval but actually isn't).
                        item.last_ts = item.next_ts - item.interval
                need_resort = True
            else:
                item.next_ts = None

        # Remove finished one-shots.
        self._schedule_interval_items = \
            [item for item in self._schedule_interval_items
             if item.next_ts is not None]

        if need_resort:
            # TODO bubble up changed items might be faster
            self._schedule_interval_items.sort(key=lambda a: a.next_ts)

        return result

    def tick(self, poll=False):
        """Signify that one frame has passed.

        This will call any scheduled functions that have elapsed.

        :Parameters:
            `poll` : bool
                If True, the function will call any scheduled functions
                but will not sleep or busy-wait for any reason.  Recommended
                for advanced applications managing their own sleep timers
                only.

                Since pyglet 1.1.

        :rtype: float
        :return: The number of seconds since the last "tick", or 0 if this was
            the first frame.
        """
        if poll:
            raise Exception('Depreciated')

        delta_t = self.update_time()
        self.call_scheduled_functions(delta_t)

        return delta_t

    def get_sleep_time(self):
        """Get the time until the next item is scheduled.

        :rtype: float
        :return: Time until the next scheduled event in seconds, or ``None``
                 if there is no event scheduled.

        :since: pyglet 1.1
        """
        if self._schedule_items:
            wake_time = self.next_ts
            if self._schedule_interval_items:
                wake_time = min(wake_time,
                                self._schedule_interval_items[0].next_ts)
            return max(wake_time - self.time(), 0.)

        if self._schedule_interval_items:
            return max(self._schedule_interval_items[0].next_ts - self.time(), 0)

    def schedule(self, func, *args, **kwargs):
        """Schedule a function to be called every frame.

        The function should have a prototype that includes ``dt`` as the
        first argument, which gives the elapsed time, in seconds, since the
        last clock tick.  Any additional arguments given to this function
        are passed on to the callback::

            def callback(dt, *args, **kwargs):
                pass

        :Parameters:
            `func` : function
                The function to call each frame.
        """
        item = _ScheduledItem(func, args, kwargs)
        self._schedule_items.append(item)

    def _schedule_item(self, func, last_ts, next_ts, interval, *args, **kwargs):
        item = _ScheduledIntervalItem(
            func, interval, last_ts, next_ts, args, kwargs)

        # Insert in sort order
        for i, other in enumerate(self._schedule_interval_items):
            if other.next_ts is not None and other.next_ts > next_ts:
                self._schedule_interval_items.insert(i, item)
                break
        else:
            self._schedule_interval_items.append(item)

    def schedule_interval(self, func, interval, *args, **kwargs):
        """Schedule a function to be called every `interval` seconds.

        Specifying an interval of 0 prevents the function from being
        called again (see `schedule` to call a function as often as possible).

        The callback function prototype is the same as for `schedule`.

        :Parameters:
            `func` : function
                The function to call when the timer lapses.
            `interval` : float
                The number of seconds to wait between each call.

        """
        last_ts = self.last_ts or self.next_ts
        ts = self.time()
        if ts - last_ts > 0.2:
            last_ts = ts

        next_ts = last_ts + interval
        self._schedule_item(func, last_ts, next_ts, interval, *args, **kwargs)

    def schedule_interval_soft(self, func, interval, *args, **kwargs):
        """Schedule a function to be called every `interval` seconds,
        beginning at a time that does not coincide with other scheduled
        events.

        This method is similar to `schedule_interval`, except that the
        clock will move the interval out of phase with other scheduled
        functions so as to distribute CPU more load evenly over time.

        This is useful for functions that need to be called regularly,
        but not relative to the initial start time.  `pyglet.media`
        does this for scheduling audio buffer updates, which need to occur
        regularly -- if all audio updates are scheduled at the same time
        (for example, mixing several tracks of a music score, or playing
        multiple videos back simultaneously), the resulting load on the
        CPU is excessive for those intervals but idle outside.  Using
        the soft interval scheduling, the load is more evenly distributed.

        Soft interval scheduling can also be used as an easy way to schedule
        graphics animations out of phase; for example, multiple flags
        waving in the wind.

        :since: pyglet 1.1

        :Parameters:
            `func` : function
                The function to call when the timer lapses.
            `interval` : float
                The number of seconds to wait between each call.

        """
        last_ts = self.last_ts or self.next_ts

        # See schedule_interval
        ts = self.time()
        if ts - last_ts > 0.2:
            last_ts = ts

        next_ts = self._get_soft_next_ts(last_ts, interval)
        last_ts = next_ts - interval
        self._schedule_item(func, last_ts, next_ts, interval, *args, **kwargs)

    def _get_soft_next_ts(self, last_ts, interval):
        def taken(ts, e):
            """Return True if the given time has already got an item
            scheduled nearby.
            """
            for item in self._schedule_interval_items:
                if item.next_ts is None:
                    pass
                elif abs(item.next_ts - ts) <= e:
                    return True
                elif item.next_ts > ts + e:
                    return False
            return False

        # Binary division over interval:
        #
        # 0                          interval
        # |--------------------------|
        #   5  3   6   2   7  4  8   1          Order of search
        #
        # i.e., first scheduled at interval,
        #       then at            interval/2
        #       then at            interval/4
        #       then at            interval*3/4
        #       then at            ...
        #
        # Schedule is hopefully then evenly distributed for any interval,
        # and any number of scheduled functions.

        next_ts = last_ts + interval
        if not taken(next_ts, interval / 4):
            return next_ts

        dt = interval
        divs = 1
        while True:
            next_ts = last_ts
            for i in range(divs - 1):
                next_ts += dt
                if not taken(next_ts, dt / 4):
                    return next_ts
            dt /= 2
            divs *= 2

            # Avoid infinite loop in pathological case
            if divs > 16:
                return next_ts

    def schedule_once(self, func, delay, *args, **kwargs):
        """Schedule a function to be called once after `delay` seconds.

        The callback function prototype is the same as for `schedule`.

        :Parameters:
            `func` : function
                The function to call when the timer lapses.
            `delay` : float
                The number of seconds to wait before the timer lapses.
        """
        last_ts = self.last_ts or self.next_ts

        ts = self.time()
        if ts - last_ts > 0.2:
            last_ts = ts

        next_ts = last_ts + delay
        self._schedule_item(func, last_ts, next_ts, 0, *args, **kwargs)

    def unschedule(self, func):
        """Remove a function from the schedule.

        If the function appears in the schedule more than once, all occurrences
        are removed.  If the function was not scheduled, no error is raised.

        :Parameters:
            `func` : function
                The function to remove from the schedule.

        """
        # First replace zombie items' func with a dummy func that does
        # nothing, in case the list has already been cloned inside tick().
        # (Fixes issue 326).
        for item in self._schedule_items:
            if item.func == func:
                item.func = _dummy_schedule_func

        for item in self._schedule_interval_items:
            if item.func == func:
                item.func = _dummy_schedule_func

        # Now remove matching items from both schedule lists.
        self._schedule_items = \
            [item for item in self._schedule_items
             if item.func is not _dummy_schedule_func]

        self._schedule_interval_items = \
            [item for item in self._schedule_interval_items
             if item.func is not _dummy_schedule_func]
