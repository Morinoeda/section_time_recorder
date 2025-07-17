import ac  # pylint: disable=E0401
from ui.base import ComponentBase

class Div(ComponentBase):
    def __init__(self, window, x, y, width, height):
        super().__init__(window, x, y, width, height)

        ac.setSize(self.component, width, height)
        ac.setPosition(self.component, x, y)
        ac.drawBorder(self.component, 0)

    def build(self, window):
        return ac.addButton(window, "")
