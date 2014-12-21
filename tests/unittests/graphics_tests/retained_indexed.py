#!/usr/bin/env python
"""Tests vertex list drawing using indexed data.
"""
import unittest

import pyglet

from tests.unittests.graphics_tests.graphics_common import GraphicsIndexedGenericTestCase
from tests.unittests.graphics_tests.graphics_common import get_feedback
from tests.unittests.graphics_tests.graphics_common import GL_TRIANGLES

__noninteractive = True


class GraphicsIndexedVertexListTestCase(GraphicsIndexedGenericTestCase,
                                        unittest.TestCase):

    def get_feedback(self, data):
        vertex_list = pyglet.graphics.vertex_list_indexed(self.n_vertices,
                                                          self.index_data,
                                                          *data)
        return get_feedback(lambda: vertex_list.draw(GL_TRIANGLES))
