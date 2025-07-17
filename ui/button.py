import functools
import ac # pylint: disable=E0401
from ui.base import ComponentBase

class Button(ComponentBase):
    def __init__(self, window, x, y, width, height, label="", on_click=None):
        super().__init__(window, x, y, width, height)
        self.callback = on_click
        self.on_click_handler = functools.partial(self.on_click)
        ac.addOnClickedListener(self.component, self.on_click_handler)

        self.set_text(label)

    def build(self, window):
        return ac.addButton(window, "")

    def set_text(self, text):
        self.label = text
        ac.setText(self.component, text)

    def set_font_alignment(self, align):
        ac.setFontAlignment(self.component, align)

    def on_click(self, *args):
        if self.callback is not None:
            self.callback()


class ToggleButton(Button):
    def __init__(self, window, x, y, width, height, label="", toggled=False, on_click=None):
        super().__init__(window, x, y, width, height, label, on_click)

        self.is_toggled = toggled

    def on_click(self, *args):
        self.is_toggled = not self.is_toggled
        return super().on_click(*args)


class ButtonGroup(object):
    class SelectableButton(Button):
        def on_click(self, *args):
            if self.callback is not None:
                self.callback(self.label)
        def set_selected(self, y):
            self.set_background_opacity(1.0 if y else 0.0)

    def __init__(self, window, x, y, width, height, labels=None, selected=None,on_click=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.labels = labels
        self.selected = selected
        self.callback = on_click
        labels = [] if labels is None else labels

        self.buttons = []
        for i, label in enumerate(labels):
            button = ButtonGroup.SelectableButton(
                window=window,
                x=x + i * width/len(labels),
                y=y,
                width=width/len(labels),
                height=height,
                label=label,
                on_click=self.on_click,
            )
            if label == self.selected:
                button.set_selected(True)
            else:
                button.set_selected(False)

            self.buttons.append(button)

    def set_visible(self, visible):
        for i, _ in enumerate(self.buttons):
            self.buttons[i].set_visible(visible)

    def on_click(self, label):
        self.selected = label
        if self.callback is not None:
            self.callback()

    def get_selected(self):
        return self.selected

    def set_selected(self, label):
        for button in self.buttons:
            if button.label == label:
                self.selected = label
                self.highlight_selected()
                break

    def highlight_selected(self):
        for i, _ in enumerate(self.buttons):
            if self.selected == self.buttons[i].label:
                self.buttons[i].set_selected(True)
            else:
                self.buttons[i].set_selected(False)
