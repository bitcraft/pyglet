#!/usr/bin/env python
"""Tests vertex list drawing.
"""
import unittest

import pyglet

from tests.unittests.graphics_tests.graphics_common import GraphicsGenericTestCase
from tests.unittests.graphics_tests.graphics_common import get_feedback
from tests.unittests.graphics_tests.graphics_common import GL_TRIANGLES

__noninteractive = True


class GraphicsVertexListTestCase(GraphicsGenericTestCase, unittest.TestCase):

    def get_feedback(self, data):
        vertex_list = pyglet.graphics.vertex_list(self.n_vertices, *data)
        return get_feedback(lambda: vertex_list.draw(GL_TRIANGLES))
