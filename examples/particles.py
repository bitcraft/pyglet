#!/usr/bin/python
# $Id:$

import random
import sys

from pyglet.gl import *
from pyglet import font
from pyglet import graphics
from pyglet import window


MAX_PARTICLES = 2000
if len(sys.argv) > 1:
    MAX_PARTICLES = int(sys.argv[1])
MAX_ADD_PARTICLES = 100
GRAVITY = -100


def add_particles():
    particle = batch.add(1, GL_POINTS, None,
                         ('v2f/stream', [win.width / 2, 0]))
    particle.dx = (random.random() - .5) * win.width / 4
    particle.dy = win.height * (.5 + random.random() * .2)
    particle.dead = False
    particles.append(particle)


def update_particles(dt):
    global particles
    for particle in particles:
        particle.dy += GRAVITY * dt
        vertices = particle.vertices
        vertices[0] += particle.dx * dt
        vertices[1] += particle.dy * dt
        if vertices[1] <= 0:
            particle.delete()
            particle.dead = True
    particles = [p for p in particles if not p.dead]


def loop(dt):
    update_particles(dt)
    for i in range(min(MAX_ADD_PARTICLES, MAX_PARTICLES - len(particles))):
        add_particles()

win = window.Window(vsync=False)
batch = graphics.Batch()
particles = list()


@win.event
def on_draw():
    win.clear()
    batch.draw()

clock = pyglet.app.event_loop.clock
clock.schedule(loop)
pyglet.app.run()
