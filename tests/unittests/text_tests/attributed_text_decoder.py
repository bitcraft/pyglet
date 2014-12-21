import unittest

from pyglet.text.formats.attributed import AttributedTextDecoder


class AttributedTextDecoderTests(unittest.TestCase):
    __noninteractive = True

    def testOneNewlineBecomesSpace(self):
        doc = AttributedTextDecoder().decode('one\ntwo')
        self.assertEqual('one two', doc.text)

    def testTwoNewlinesBecomesParagraph(self):
        from pyglet.text.formats.attributed import AttributedTextDecoder

        doc = AttributedTextDecoder().decode('one\n\ntwo')
        self.assertEqual('one\ntwo', doc.text)
