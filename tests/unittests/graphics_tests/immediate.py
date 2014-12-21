#!/usr/bin/env python
"""Tests immediate drawing.
"""
import unittest

import pyglet

from tests.unittests.graphics_tests.graphics_common import GraphicsGenericTestCase
from tests.unittests.graphics_tests.graphics_common import get_feedback
from tests.unittests.graphics_tests.graphics_common import GL_TRIANGLES

__noninteractive = True


class GraphicsImmediateTestCase(GraphicsGenericTestCase, unittest.TestCase):

    def get_feedback(self, data):
        return get_feedback(
            lambda: pyglet.graphics.draw(self.n_vertices, GL_TRIANGLES, *data))
