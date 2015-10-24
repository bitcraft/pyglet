# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
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

"""Scheduler

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


If you want to schedule a function that doesn't accept the dt argument, you can
use a `lambda
<http://docs.python.org/2/reference/expressions.html#lambda>`_ expression
to write a short function that does accept dt. For Example::

    def no_args_func():
        print("I accept no arguments, so don't schedule me in the clock")

    Clock.schedule_once(lambda dt: no_args_func(), 0.5)


Using multiple clocks
=====================

Each clock maintains its own set of scheduled functions and must be
"ticked" separately.

Multiple and derived clocks potentially allow you to separate "game-time" and
"wall-time", or to synchronise your clock to an audio or video stream instead
of the system clock.
"""
import collections
import time
from operator import attrgetter
from heapq import heappush, heapify, heappop, heappushpop


class ScheduledItem:
    """ A class that describes a scheduled callback.

    This class is never created by the user; instead, pyglet creates and
    returns an instance of this class when scheduling a callback.

   .. warning::
   Most of the methods of this class are internal and can change without
   notice.

    """
    __slots__ = ['func', 'interval', 'last_ts', 'next_ts', 'args', 'kwargs']

    def __init__(self, func, args, kwargs, last_ts=0, next_ts=0, interval=0):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.interval = interval
        self.last_ts = last_ts
        self.next_ts = next_ts

    def __lt__(self, other):
        try:
            return self.next_ts < other.next_ts
        except AttributeError:
            return self.next_ts < other


class Scheduler:
    """Class for scheduling functions.
    """

    def __init__(self, time_function=time.perf_counter):
        """Initialise a Clock, with optional custom time function.

        :Parameters:
            `time_function` : function
                Function to return the elapsed time of the application,
                in seconds.  Defaults to platform dependant clock, but can be
                replaced to allow for easy time dilation effects, game pausing,
                or testing.

        """
        super().__init__()
        self._time = time_function
        self._last_ts = -1
        self._times = collections.deque(maxlen=10)
        self._scheduled_items = list()
        self._every_tick_items = list()
        self.cumulative_time = 0

    def _get_nearest_ts(self):
        """Schedule from now, unless now is sufficiently close to last_ts, in
        which case use last_ts.  This clusters together scheduled items that
        probably want to be scheduled together.  The old (pre 1.1.1)
        behaviour was to always use self.last_ts, and not look at ts.  The
        new behaviour is needed because clock ticks can now be quite
        irregular, and span several seconds.
        """
        last_ts = self._last_ts
        ts = self._time()
        if ts - last_ts > 0.2:
            last_ts = ts
        return last_ts

    def _get_soft_next_ts(self, last_ts, interval):
        def taken(ts, e):
            """Return True if the given time has already got an item
            scheduled nearby.
            """
            # TODO this function is slow and called very often.  optimise it, maybe?
            for item in sorted_items:
                if abs(item.next_ts - ts) <= e:
                    return True
                elif item.next_ts > ts + e:
                    return False

            return False

        # sorted list is required required to produce expected results
        # taken() will iterate through the heap, expecting it to be sorted
        # and will not always catch smallest value, so create a sorted variant here
        # NOTE: do not rewrite as popping from heap, as that is super slow!
        sorted_items = sorted(self._scheduled_items, key=attrgetter('next_ts'))

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

    def schedule(self, func, *args, **kwargs):
        """Schedule a function to be called every tick.

        The function should have a prototype that includes ``dt`` as the
        first argument, which gives the elapsed time, in seconds, since the
        last clock tick.  Any additional arguments given to this function
        are passed on to the callback::

            def callback(dt, *args, **kwargs):
                pass

        :Parameters:
            `func` : function
                The function to call each tick.
        """
        item = ScheduledItem(func, args, kwargs)
        self._every_tick_items.append(item)

    def schedule_once(self, func, delay, *args, **kwargs):
        """Schedule a function to be called once after `delay` seconds.

        The callback function prototype is the same as for `schedule`.

        :Parameters:
            `func` : function
                The function to call when the timer lapses.
            `delay` : float
                The number of seconds to wait before the timer lapses.
        """
        last_ts = self._get_nearest_ts()
        next_ts = last_ts + delay
        item = ScheduledItem(func, args, kwargs, last_ts, next_ts, 0)
        heappush(self._scheduled_items, item)

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
        last_ts = self._get_nearest_ts()
        next_ts = last_ts + interval
        item = ScheduledItem(func, args, kwargs, last_ts, next_ts, interval)
        heappush(self._scheduled_items, item)

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
        next_ts = self._get_soft_next_ts(self._get_nearest_ts(), interval)
        last_ts = next_ts - interval
        item = ScheduledItem(func, args, kwargs, last_ts, next_ts, interval)
        heappush(self._scheduled_items, item)

    def tick(self):
        """Cause clock to update self and call scheduled functions.

        This updates the clock's internal measure of time and returns
        the difference since the last update (or since the clock was created).

        Will call any scheduled functions that have elapsed.

        :rtype: float
        :return: The number of seconds since the last "tick", or 0 if this was
                 the first tick.
        """
        delta_t = self.set_time(self._time())
        self._times.append(delta_t)
        self.call_scheduled_functions(delta_t)
        return delta_t

    def get_interval(self):
        """Get the average amount of time passed between each tick.

        Useful for calculating FPS if this clock is used with the display.
        Returned value is averaged from last 10 ticks.

        Value will be zero if before 1st tick.

        :rtype: float
        :return: The number of seconds since the last "tick", or 0 if this was
                 the first tick.
        """
        try:
            return sum(self._times) / len(self._times)
        except ZeroDivisionError:
            return 0.0

    def set_time(self, time_stamp):
        """Set the clock manually and do not call scheduled functions.  Return
        the difference in time from the last time clock was updated.

        :Parameters:
            `time_stamp` : float
                This will become the new value of the clock.  Setting the clock
                to negative values will have undefined results.

        :rtype: float
        :return: The number of seconds since the last update, or 0 if this was
                 the first update.

        """
        # self._last_ts will be -1 before first time set
        if self._last_ts < 0:
            delta_t = 0
            self._last_ts = time_stamp
        else:
            delta_t = time_stamp - self._last_ts
        self.cumulative_time += delta_t
        self._last_ts = time_stamp
        return delta_t

    def call_scheduled_functions(self, dt):
        """Call scheduled functions that elapsed during the last `update_time`.

        :since: pyglet 1.2

        :Parameters:
            dt : float
                The elapsed time since the last update to pass to each
                scheduled function.  This is *not* used to calculate which
                functions have elapsed.

        :rtype: bool
        :return: True if any functions were called, otherwise False.
        """
        scheduled_items = self._scheduled_items
        now = self._last_ts
        result = False  # flag indicates if any function was called

        # handle items scheduled for every tick
        if self._every_tick_items:
            result = True
            # duplicate list in case event unschedules itself
            for item in list(self._every_tick_items):
                item.func(dt, *item.args, **item.kwargs)

        # check the next scheduled item that is not called each tick
        # if it is scheduled in the future, then exit
        try:
            if scheduled_items[0].next_ts > now:
                return result

        # raised when the scheduled_items list is empty
        except IndexError:
            return result

        # whenever 'replace' is true the current item will be pushed
        # into the heap.  it essentially means that the current
        # scheduled item is important and needs stay scheduled.
        # its use is to reduce heap operations
        replace = False
        item = None

        get_soft_next_ts = self._get_soft_next_ts
        while scheduled_items:

            # the scheduler will hold onto a reference to an item in
            # case it needs to be rescheduled.  it is more efficient
            # to push and pop the heap at once rather than two operations
            if replace:
                item = heappushpop(scheduled_items, item)
            else:
                item = heappop(scheduled_items)

            # if next item is scheduled in the future then break
            if item.next_ts > now:
                replace = True
                break

            # execute the callback
            item.func(now - item.last_ts, *item.args, **item.kwargs)

            if item.interval:
                # this item needs to be pushed back onto the heap
                replace = True

                # Try to keep timing regular, even if overslept this time;
                # but don't schedule in the past (which could lead to
                # infinitely-worsening error).
                item.next_ts = item.last_ts + item.interval
                item.last_ts = now

                # test the schedule for the next execution
                if item.next_ts <= now:
                    # the scheduled time of this item has already passed
                    # so it must be rescheduled
                    if now - item.next_ts < 0.05:
                        # missed execution time by 'reasonable' amount, so
                        # reschedule at normal interval
                        item.next_ts = now + item.interval
                    else:
                        # missed by significant amount, now many events have
                        # likely missed execution. do a soft reschedule to
                        # avoid lumping many events together.
                        # in this case, the next dt will not be accurate
                        item.next_ts = get_soft_next_ts(now, item.interval)
                        item.last_ts = item.next_ts - item.interval
            else:
                # not an interval, so this item will not be rescheduled
                replace = False

        if replace:
            heappush(scheduled_items, item)

        return True

    def get_sleep_time(self):
        """Get the time until the next item is scheduled.

        :rtype: float
        :return: Time until the next scheduled event in seconds, or ``None``
                 if there is no event scheduled.

        :since: pyglet 1.1
        """
        if self._every_tick_items:
            return 0

        try:
            next_ts = self._scheduled_items[0].next_ts
            return max(next_ts - self._time(), 0.)
        except IndexError:
            return None

    def unschedule(self, func):
        """Remove a function from the schedule.

        If the function appears in the schedule more than once, all occurrences
        are removed.  If the function was not scheduled, no error is raised.

        :Parameters:
            `func` : function
                The function to remove from the schedule.
        """
        # clever remove item with disturbing the heap:
        # 1. set function to an empty lambda -- original function is not call
        # 2. set interval to 0               -- item will be removed from heap eventually
        for item in set(item for item in self._scheduled_items if item.func is func):
            item.interval = 0
            item.func = lambda x: x

        self._every_tick_items = [i for i in self._every_tick_items if i.func is not func]


class Clock(Scheduler):
    """Schedules stuff like a Scheduler, and includes time limiting functions
    """
