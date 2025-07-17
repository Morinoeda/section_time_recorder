import ac # pylint: disable=E0401

class ComponentBase(object):
    def __init__(self, window, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.component = self.build(window)
        self.set_position(x, y)
        self.set_size(width, height)

    def set_size(self, width, height):
        self.width = width
        self.height = height
        ac.setSize(self.component, width, height)

    def set_position(self, x, y):
        self.x = x
        self.y = y
        ac.setPosition(self.component, x, y)

    def set_background_color(self, r, g, b):
        ac.setBackgroundColor(self.component, r, g, b)

    def set_background_opacity(self, opacity):
        ac.setBackgroundOpacity(self.component, opacity)

    def draw_background(self, enable):
        ac.drawBackground(self.component, 1 if enable else 0)

    def draw_boarder(self, enable):
        ac.drawBorder(self.component, 1 if enable else 0)

    def set_visible(self, visible):
        ac.setVisible(self.component, 1 if visible else 0)

    def build(self, window):
        raise NotImplementedError("build not implemented")
