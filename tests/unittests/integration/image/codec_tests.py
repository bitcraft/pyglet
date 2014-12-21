__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import unittest
from os.path import dirname, join, abspath

from pyglet import image
from pyglet.image import Texture

png_files = ['l.png',
             'la.png',
             'rgb.png',
             'rgba.png',
             'rgb_8bpp.png',
             'rgb_8bpp_trans.png']

dds_files = ['rgb_dxt1.dds',
             'rgba_dxt1.dds',
             'rgba_dxt3.dds',
             'rgba_dxt5.dds']

bmp_files = ['rgb_1bpp.bmp',
             'rgb_4bpp.bmp',
             'rgb_8bpp.bmp',
             'rgb_16bpp.bmp',
             'rgb_24bpp.bmp',
             'rgb_32bpp.bmp',
             'rgba_32bpp.bmp']

gif_files = ['8bpp.gif']


class TestImageCodecs(unittest.TestCase):
    def _test_load(self, filenames, decoder, convert=False):
        for filename in filenames:
            filename = abspath(join(dirname(__file__),
                                    '../../../data/images', filename))
            try:
                data = image.load(filename, decoder=decoder)
                if convert:
                    data.create_texture(Texture)
            except:
                raise

    def test_pypng_load(self):
        from pyglet.image.codecs.png import PNGImageDecoder
        self._test_load(png_files, PNGImageDecoder(), True)

    def test_pil_load(self):
        from pyglet.image.codecs.pil import PILImageDecoder
        self._test_load(png_files, PILImageDecoder(), True)

    def test_gdkpixbuf2_load(self):
        from pyglet.image.codecs.gdkpixbuf2 import GdkPixbuf2ImageDecoder
        self._test_load(gif_files, GdkPixbuf2ImageDecoder(), True)

    def test_dds_load(self):
        from pyglet.image.codecs.dds import DDSImageDecoder
        self._test_load(dds_files, DDSImageDecoder())

    def test_bmp_load(self):
        from pyglet.image.codecs.bmp import BMPImageDecoder
        self._test_load(bmp_files, BMPImageDecoder(), True)

    def test_pypng_save(self):
        from pyglet.image.codecs.png import PNGImageEncoder
        encoder = PNGImageEncoder()

