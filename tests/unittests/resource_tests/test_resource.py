def get_settings_path(name):
    """Get a directory to save user preferences.

    Different platforms have different conventions for where to save user
    preferences, saved games, and settings.  This function implements those
    conventions.  Note that the returned path may not exist: applications
    should use ``os.makedirs`` to construct it if desired.

    On Linux, a directory `name` in the user's configuration directory is
    returned (usually under ``~/.config``).

    On Windows (including under Cygwin) the `name` directory in the user's
    ``Application Settings`` directory is returned.

    On Mac OS X the `name` directory under ``~/Library/Application Support``
    is returned.

    :Parameters:
        `name` : str
            The name of the application.

    :rtype: str
    """
    jpath = os.path.join

    def get_home():
        return os.path.expanduser('~')

    path = None
    if pyglet.compat_platform in ('cygwin', 'win32'):
        if 'APPDATA' in os.environ:
            path = os.environ['APPDATA']
        else:
            path = get_home()
        return jpath(path, )
    elif pyglet.compat_platform == 'darwin':
        path = os.path.expanduser('~/Library/Application Support')
    elif pyglet.compat_platform.startswith('linux'):
        if 'XDG_CONFIG_HOME' in os.environ:
            path = os.path.join(os.environ['XDG_CONFIG_HOME'])
        else:
            path = os.path.expanduser('~/.config')
    else:
        path = os.path.expanduser('~')

    if path is None:
        raise Exception

    return os.path.join(path, name)


import unittest
import mock
import importlib
import os
import sys
import pyglet


class TestResource(unittest.TestCase):
    name = 'pyglet'

    @mock.patch("sys.platform", "linux")
    def test_get_settings_path_linux(self):
        importlib.reload(pyglet)
        self.assertEqual('linux', pyglet.compat_platform)
        path = pyglet.resource.get_settings_path(self.name)
        print(path)

    @mock.patch("sys.platform", "unix")
    def test_get_settings_path_unix(self):
        importlib.reload(pyglet)
        self.assertEqual('unix', pyglet.compat_platform)
        path = pyglet.resource.get_settings_path(self.name)
        print(path)

    @mock.patch("sys.platform", "darwin")
    @mock.patch("platform.mac_ver", lambda: ['10.10.0'])  # supported version
    @mock.patch('struct.calcsize', lambda i: 8)           # pass the 64-bit test
    def test_get_settings_path_osx(self):
        importlib.reload(pyglet)
        self.assertEqual('darwin', pyglet.compat_platform)
        path = pyglet.resource.get_settings_path(self.name)
        print(path)

    @mock.patch("sys.platform", "win32")
    def test_get_settings_path_windows(self):
        importlib.reload(pyglet)
        self.assertEqual('win32', pyglet.compat_platform)
        path = pyglet.resource.get_settings_path(self.name)
        print(path)

    @mock.patch("sys.platform", "cygwin")
    def test_get_settings_path_cygwin(self):
        importlib.reload(pyglet)
        self.assertEqual('cygwin', pyglet.compat_platform)
        path = pyglet.resource.get_settings_path(self.name)
        print(path)
