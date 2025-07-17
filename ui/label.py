import ac # pylint: disable=E0401
from ui.base import ComponentBase

class Label(ComponentBase):
    def __init__(self, window, x=0, y=0, width=0, height=0,
                 text="", font_size=14, font_align="left"):
        super().__init__(window, x, y, width, height)

        self.set_text(text)
        self.set_font_size(font_size)
        self.set_font_alignment(font_align)

    def build(self, window):
        return ac.addLabel(window, "")

    def set_text(self, text):
        self.text = text
        ac.setText(self.component, text)

    def set_font_size(self, size):
        ac.setFontSize(self.component, size)

    def set_custom_font(self, family="Arial", italic=False, bold=False):
        ac.setCustomFont(self.component, family, 1 if italic else 0, 1 if bold else 0)

    def set_font_alignment(self, alignment):
        ac.setFontAlignment(self.component, alignment)
