from ui.label import Label
from ui.window import Window
from ui.pager import VerticalPager
from ui.utils import milliseconds_to_time_string

class LaptimeApp(Window):
    def __init__(self, name, width=380, height=400, per_page=5):
        super().__init__(name, width, height)

        self.per_page=per_page

        self.top_margin = 50

        self.total_time_label = Label(
            window=self.window,
            x=0,
            y=self.top_margin+20,
            width=150,
            height=40,
            font_size=20,
            text="Total Time"
        )
        self.total_time_label.set_custom_font(italic=True, bold=True)

        self.total_time = Label(
            window=self.window,
            x=self.total_time_label.x + self.total_time_label.width,
            y=self.top_margin,
            width=200,
            height=40,
            font_size=45,
            text="-- \' -- \" ---"
        )

        self.section_time_title_label = Label(
            window=self.window,
            x=0,
            y=self.top_margin + self.total_time.height + 20,
            width=150,
            height=40,
            font_size=20,
            text="Section Time"
        )
        self.section_time_title_label.set_custom_font(italic=True, bold=True)

        self.section_times = []
        self.section_time_labels = []
        base_y = self.total_time.y + self.total_time.height + 50
        for i in range(self.per_page):
            label = Label(
                window=self.window,
                x=50,
                y=base_y + 40 * i,
                width=200,
                height=30,
                font_size=32
            )
            label.set_text("")
            self.section_time_labels.append(label)

        self.pager = VerticalPager(
            window=self.window,
            x=width-40,
            y=self.section_time_title_label.y + self.section_time_title_label.height,
            width=40,
            height=self.height,
            on_change=self.on_change_spinner,
        )

        self.set_background_opacity(0)

    def set_lap_time(self, milliseconds):
        self.total_time.set_text(milliseconds_to_time_string(milliseconds))

    def append_section_time(self, milliseconds):
        self.section_times.append(milliseconds)

        if len(self.section_times) % self.per_page  == 0:
            npages = len(self.section_times) // self.per_page
        else:
            npages = 1 + len(self.section_times) // self.per_page

        self.pager.set_max_number(npages)
        offset = self.per_page * (npages - 1)

        self.pager.set_tail()
        for i in range(self.per_page):
            try:
                t = self.section_times[offset+i]
                self.section_time_labels[i].set_text(
                    "{:>3}:         {}".format(offset + i + 1, milliseconds_to_time_string(t)))
            except IndexError:
                # This exception is expected if section time array length is less than
                # 'self.per_page'. Leave the label empty.
                self.section_time_labels[i].set_text("")

    def clear(self):
        self.total_time.set_text("-- \' -- \" ---")
        self.section_times.clear()
        for label in self.section_time_labels:
            label.set_text("")

    def on_change_spinner(self):
        page = self.pager.get_value()
        if page > 0:
            offset = self.per_page * (page - 1)
            for i in range(self.per_page):
                try:
                    t = self.section_times[offset + i]
                    self.section_time_labels[i].set_text("{:>3}:         {}".format(
                                offset + i + 1, milliseconds_to_time_string(t)))
                except IndexError:
                    # This exception is expected if section time array length is less than
                    # 'self.per_page'. clear the label
                    self.section_time_labels[i].set_text("")
