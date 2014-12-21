import pyglet

# Cocoa implementation:
if pyglet.options['darwin_cocoa']:
    from .cocoapy import *
