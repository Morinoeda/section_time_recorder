from ui.button import Button
from ui.label import Label

class PagerBase:
    def __init__(self, window, x, y, width, height, font_size=16,
                 max_number=None, empty_label="", on_change=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font_size = font_size

        self.on_change_handler = on_change
        self.current_number = 0
        self.max_number = max_number
        self.empty_label = empty_label

        self.prev_button = self.generate_prev_button(window)
        self.number_label = self.generate_number_label(window)
        self.next_button = self.generate_next_button(window)

        self.next_button.draw_boarder(False)
        self.prev_button.draw_boarder(False)
        self.number_label.set_text(empty_label)
        self.number_label.set_font_size(font_size)

    def generate_prev_button(self, window) -> Button:
        raise NotImplementedError()
    def generate_next_button(self, window) -> Button:
        raise NotImplementedError()
    def generate_number_label(self, window) -> Label:
        raise NotImplementedError

    def _set_empty(self):
        self.max_number = 0
        self.current_number = 0
        self.number_label.set_text(self.empty_label)

    def _set_value(self, value):
        self.current_number = value
        self.number_label.set_text("{} / {}".format(self.current_number, self.max_number))

    def set_head(self):
        self._set_value(1)

    def set_tail(self):
        self._set_value(self.max_number)

    def increment(self):
        if self.current_number + 1 <= self.max_number and self.max_number > 0:
            self._set_value(self.current_number + 1)

    def decrement(self):
        if 0 < self.current_number - 1 and self.max_number > 0:
            self._set_value(self.current_number - 1)

    def get_value(self):
        return self.current_number

    def set_visible(self, visible):
        self.prev_button.set_visible(visible)
        self.next_button.set_visible(visible)
        self.number_label.set_visible(visible)

    def set_max_number(self, n):
        self.max_number = n
        if self.max_number == 0:
            self._set_empty()
        elif self.current_number == 0:
            self._set_value(1)
        elif self.max_number < self.current_number:
            self._set_value(self.max_number)
        else:
            self._set_value(self.current_number)

    def on_click_prev(self):
        if self.on_change_handler is not None:
            self.decrement()
            self.on_change_handler()

    def on_click_next(self):
        if self.on_change_handler is not None:
            self.increment()
            self.on_change_handler()

class HorizontalPager(PagerBase):
    def generate_prev_button(self, window):
        return Button(
            window=window,
            x=self.x,
            y=self.y,
            width=self.height,
            height=self.height,
            label="<",
            on_click=self.on_click_prev
        )

    def generate_number_label(self, window):
        return Label(
            window=window,
            x=self.x + self.height,
            y=self.y,
            width=self.width-self.height*2,
            height=self.height,
            text="",
            font_size=self.font_size,
            font_align="center"
        )

    def generate_next_button(self, window):
        return Button(
            window=window,
            x=self.x + self.width - self.height,
            y=self.y,
            width=self.height,
            height=self.height,
            label=">",
            on_click=self.on_click_next
        )

class VerticalPager(PagerBase):
    def generate_prev_button(self, window):
        return Button(
            window=window,
            x=self.x,
            y=self.y,
            width=self.width,
            height=self.width,
            label="<",
            on_click=self.on_click_prev
        )

    def generate_number_label(self, window):
        return Label(
            window=window,
            x=self.x,
            y=self.y + self.width,
            width=self.width,
            height=self.height - self.width*2,
            text="",
            font_size=self.font_size,
            font_align="center"
        )

    def generate_next_button(self, window):
        return Button(
            window=window,
            x=self.x,
            y=self.height - self.width,
            width=self.width,
            height=self.width,
            label=">",
            on_click=self.on_click_next
        )
