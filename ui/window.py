import ac # pylint: disable=E0401

class Window(object):
    def __init__(self, name, width, height):
        self.window = ac.newApp(name)
        self.name = name
        self.width = width
        self.height = height

        ac.setSize(self.window, width, height)

        # disable the window border
        ac.drawBorder(self.window, 0)

        ac.setTitle(self.window, "")

        # move the assetto corsa icon out of sight
        ac.setIconPosition(self.window, 0, -10000)

        ac.drawBackground(self.window, 1)
        ac.setBackgroundColor(self.window, 0.149, 0.156, 0.145)
        ac.setBackgroundOpacity(self.window, 0.9)

        self.components = []

    def set_size(self, width, height):
        self.width = width
        self.height = height
        ac.setSize(self.window, width, height)

    def set_background_rgba(self, r, g, b):
        ac.setBackgroundColor(self.window, r, g, b)

    def set_background_opacity(self, opacity):
        ac.setBackgroundOpacity(self.window, opacity)
