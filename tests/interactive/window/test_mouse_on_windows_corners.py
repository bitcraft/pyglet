"""
Moves the mouse to the four window corner and tells
wheter each corner was seen in an on_mouse_move event.

Instructions:
    Move a bit the mouse near window center
    Left alone the mouse in that position
    Press any key
    Wait a few seconds for the program to terminate
    The last lines in console should report the results.
"""
# Note: while the script does not call anything Windows specific, it relays on
# the fact that window.set_mouse_position triggers an on_mouse_move event.
# Don't know if the assuption holds in other OS

from __future__ import print_function, unicode_literals, division
import pyglet
import pyglet.clock

width = 640
height = 480
# window's corners in pyglet coords
corners= {
    'bottomleft': (0, 0),
    'bottomright': (width-1, 0),
    'topright': (width-1, height-1),
    'topleft': (0, height-1)
    }
names = [k for k in corners]
coords_received = set()
sequencer_activated = False

window = pyglet.window.Window(width, height, resizable=False)
label = pyglet.text.Label(__doc__,
                         font_size=14 ,
                         width=width,
                         x=50, y=height * 3 // 4,
                         multiline=True)
@window.event
def on_draw():
    window.clear()
    label.draw()


def mouse_move_sequencer(dt):
    global names
    if names:
        name = names.pop()
        x, y = corners[name]
        print('moving to', name)
        window.set_mouse_position(x, y)
    else:
        names = [k for k in corners]
        print("Results:")
        for name in names:
            if corners[name] in coords_received:
                print(name, ': ok, received in on_mouse_move')
            else:
                print(name, ': ERROR, not received in on_mouse_move')
        pyglet.app.exit()

@window.event
def on_mouse_motion(x, y, *args, **kwargs):
    print("x, y:", x, y)
    coords_received.add((x,y))

@window.event
def on_key_release(key, modifiers):
    global sequencer_activated
    if not sequencer_activated:
        sequencer_activated = True
        print("test begin")
        pyglet.app.event_loop.clock.schedule_interval(mouse_move_sequencer, 1.0)

pyglet.app.run()
