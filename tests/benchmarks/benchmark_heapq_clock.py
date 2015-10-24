"""
Test pyglet's clock vs. clock implementation with heapq.

A random list of items to be scheduled is created for each test run and the
benchmark will simulate time passing and scheduling of items.

The purpose of this is to investigate if using a heapq is faster for insertion
of scheduled elements and for sorting the scheduled items queue.
"""


def generate_events(clock):
    from random import randrange, choice

    def make_function():
        def _(dt):
            pass
        return _

    def kill(clock, f):
        def _(dt):
            clock.unschedule(f)
        return _

    # make a bunch of schedulable functions
    pool = [make_function() for i in range(200)]

    # randomly each-tick schedule them
    for i in range(10):
        clock.schedule(choice(pool))

    # # randomly schedule interval them
    for i in range(500):
        clock.schedule_interval(choice(pool), randrange(0, 1000))

    # randomly soft_schedule them
    for i in range(20):
        clock.schedule_interval_soft(choice(pool), randrange(0, 1000))

    # randomly schedule 25% of all events to be unscheduled
    for i, f in enumerate(pool[:len(pool) // 4]):
        clock.schedule_once(kill(clock, f), randrange(500, 1000))


def benchmark(class_):
    time = 0
    clock = class_(lambda: time)
    generate_events(clock)
    for time in range(1000):
        clock.tick()


if __name__ == '__main__':
    setup = """from __main__ import benchmark
from pyglet.clock import Clock as HeapClock
from clocklegacy import Clock as LegacyClock"""

    import timeit
    result = timeit.repeat("benchmark(HeapClock)", setup, repeat=5, number=5)
    heap_time = max(result)

    result = timeit.repeat("benchmark(LegacyClock)", setup, repeat=5, number=5)
    legacy_time = max(result)

    _min, _max = sorted((heap_time, legacy_time))
    diff = ((_max - _min) / _max) * 100.0

    print('max time to execute:')
    print("heap:\t{}\nold:\t{}\ndiff:\t{}".format(heap_time, legacy_time, diff))

