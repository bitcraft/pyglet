import unittest
import mock
import importlib
import pyglet


# TODO: Fill in some meaningful tests for this test case
class SettingsPathTestCase(unittest.TestCase):
    name = 'pyglet'

    @mock.patch("sys.platform", "linux")
    def test_get_settings_path_linux(self):
        importlib.reload(pyglet)
        self.assertEqual('linux', pyglet.compat_platform)
        path = pyglet.resource.get_settings_path(self.name)

    @mock.patch("sys.platform", "bsd")
    def test_get_settings_path_unix(self):
        importlib.reload(pyglet)
        self.assertEqual('linux-compat', pyglet.compat_platform)
        path = pyglet.resource.get_settings_path(self.name)

    @mock.patch("sys.platform", "darwin")
    @mock.patch("platform.mac_ver", lambda: ['10.10.0'])  # supported version
    @mock.patch('struct.calcsize', lambda i: 8)           # pass the 64-bit test
    def test_get_settings_path_osx(self):
        importlib.reload(pyglet)
        self.assertEqual('darwin', pyglet.compat_platform)
        path = pyglet.resource.get_settings_path(self.name)

    @mock.patch("os.environ", dict())
    @mock.patch("sys.platform", "win32")
    def test_get_settings_path_windows_cygwin(self):
        importlib.reload(pyglet)
        self.assertEqual('win32', pyglet.compat_platform)
        path = pyglet.resource.get_settings_path(self.name)

    @mock.patch("sys.platform", "cygwin")
    def test_get_settings_path_cygwin(self):
        bogus_path = 'C:\Bob\Run\\'
        importlib.reload(pyglet)
        self.assertEqual('cygwin', pyglet.compat_platform)
        with mock.patch("os.environ", {'APPDATA': bogus_path}) as p:
            path = pyglet.resource.get_settings_path(self.name)
            self.assertTrue(path.startswith(bogus_path))
        with mock.patch("os.environ", dict()) as p:
            path = pyglet.resource.get_settings_path(self.name)
            self.assertFalse(path.startswith(bogus_path))


