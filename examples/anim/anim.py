import pyglet

def center_anchor(img):
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2

class TestSprite(pyglet.sprite.Sprite):
    def __init__(self, x, y):
        images = []
        n = range(1,21)
        for i in n:
            img = pyglet.resource.image('%04d.png' % i)
            center_anchor(img)
            images.append(img)
        self.forward = pyglet.image.Animation.from_image_sequence(images, 1/60.0, loop=False)
        images.reverse()
        self.backward = pyglet.image.Animation.from_image_sequence(images, 1/60.0, loop=False)
        super(TestSprite, self).__init__(self.forward, x, y)
        self.goback = False
        self.goforward = False

    def on_animation_end(self):
        pass

    def update(self):
        if self.goback:
            self.image = sprite.backward
            self.goback = False
        if self.goforward:
            self.image = sprite.forward
            self.goforward = False

window = pyglet.window.Window()
sprite = TestSprite(window.width//2, window.height//2)

@window.event
def on_draw():
    window.clear()
    sprite.draw()

@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.Z:
        sprite.goback = True
    if symbol == pyglet.window.key.X:
        sprite.goforward = True

def update(dt):
    sprite.update()

pyglet.app.event_loop.clock.schedule_interval(update, 1/60.)

pyglet.app.run()
