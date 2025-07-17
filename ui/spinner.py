import ac # pylint: disable=E0401
from ui.base import ComponentBase

class Spinner(ComponentBase):
    def __init__(self, window, x, y, width, height, min_value=0.0, max_value=0.0):
        super().__init__(window, x, y, width, height)

        self.min_value = min_value
        self.max_value = max_value

        self.set_rage(self.min_value, self.max_value)

    def build(self, window):
        return ac.addSpinner(window, "")

    def set_rage(self, min_value=None, max_value=None):
        if min_value is None:
            min_value = self.min_value
        if max_value is None:
            max_value = self.max_value

        ac.setRange(self.component, self.min_value, self.max_value)

    def set_value(self, value):
        if self.min_value <= value <= self.max_value:
            ac.setValue(self.component, value)
