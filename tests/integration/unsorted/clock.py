def test_clock():
    import getopt
    import sys

    test_seconds = 1
    test_fps = 60
    show_fps = False
    options, args = getopt.getopt(sys.argv[1:], 'vht:f:',
                                  ['time=', 'fps=', 'help'])
    for key, value in options:
        if key in ('-t', '--time'):
            test_seconds = float(value)
        elif key in ('-f', '--fps'):
            test_fps = float(value)
        elif key in ('-v'):
            show_fps = True
        elif key in ('-h', '--help'):
            print('Usage: clock.py <options>\n'
                  '\n'
                  'Options:\n'
                  '  -t   --time       Number of seconds to run for.\n'
                  '  -f   --fps        Target FPS.\n'
                  '\n'
                  'Tests the clock module by measuring how close we can\n'
                  'get to the desired FPS by sleeping and busy-waiting.')
            sys.exit(0)

    set_fps_limit(test_fps)
    start = time.time()

    # Add one because first frame has no update interval.
    n_frames = int(test_seconds * test_fps + 1)

    print('Testing %f FPS for %f seconds...' % (test_fps, test_seconds))
    for i in range(n_frames):
        tick()
        if show_fps:
            print(get_fps())
    total_time = time.time() - start
    total_error = total_time - test_seconds
    print('Total clock error: %f secs' % total_error)
    print('Total clock error / secs: %f secs/secs' %
          (total_error / test_seconds))

    # Not fair to add the extra frame in this calc, since no-one's interested
    # in the startup situation.
    print('Average FPS: %f' % ((n_frames - 1) / total_time))

    test_clock()
