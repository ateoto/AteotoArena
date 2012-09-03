import sfml as sf


class UIElement(object):
    pass


class UI(object):
    def __init__(self, size):
        self.texture = sf.RenderTexture(size.x, size.y)

    def update(self, dt):
        pass
