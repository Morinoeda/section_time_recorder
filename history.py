from ui.label import Label
from ui.pager import HorizontalPager, VerticalPager
from ui.window import Window
from ui.utils import milliseconds_to_time_string

class HistoryApp(Window):
    def __init__(self, name, width=380, height=400, per_page=5):
        super().__init__(name, width, height)
        self.top_margin = 50

        self.lap_pager = HorizontalPager(
            window=self.window,
            x=0,
            y=self.top_margin,
            width=width,
            height=40,
            font_size=30,
            on_change=self.on_change_lap_time_pager,
        )

        self.total_time_label = Label(
            window=self.window,
            x=0,
            y=self.lap_pager.y+self.lap_pager.height,
            width=150,
            height=40,
            font_size=20,
            text="Total Time"
        )
        self.total_time_label.set_custom_font(italic=True, bold=True)

        self.total_time = Label(
            window=self.window,
            x=self.total_time_label.x + self.total_time_label.width,
            y=self.lap_pager.y+self.lap_pager.height,
            width=200,
            height=40,
            font_size=45,
            text="-- \' -- \" ---"
        )

        self.section_time_pager = VerticalPager(
            window=self.window,
            x=width - 40,
            y=self.total_time_label.y + self.total_time_label.height,
            width=40,
            height=height-self.total_time_label.y,
            on_change=self.on_change_section_time_pager
        )

        self.section_time_label = Label(
            window=self.window,
            x=0,
            y=self.total_time_label.y + self.total_time_label.height,
            width=150,
            height=40,
            font_size=20,
            text="Section Time"
        )
        self.section_time_label.set_custom_font(italic=True, bold=True)

        self.laps = []
        self.section_labels = []
        for i in range(per_page):
            self.section_labels.append(Label(
                window=self.window,
                x=50,
                y=self.section_time_label.y + self.section_time_label.height + 50*i,
                width=150,
                height=40,
                font_size=32,
                text=""
            ))

    def append(self, lap_count, section_times):
        self.laps.append({
            "lap_count": lap_count,
            "section_times": section_times
        })

        self.lap_pager.set_max_number(len(self.laps))
        lap_time_page = self.lap_pager.get_value()
        section_time_count = len(self.laps[lap_time_page- 1]["section_times"])
        npages = section_time_count // len(self.section_labels)
        if section_time_count % len(self.section_labels) != 0:
            npages = npages + 1
        self.section_time_pager.set_max_number(npages)
        self.show(self.lap_pager.get_value())

    def delete(self):
        self.lap_pager.max_number(0)
        self.section_time_pager.max_number(0)
        self.laps.clear()
        self.section_labels.clear()

    def show(self, lap_time_page, section_time_page=1):
        offset = len(self.section_labels) * (section_time_page - 1)
        total_milliseconds = 0
        for i, _ in enumerate(self.section_labels):
            try:
                section_time = self.laps[lap_time_page- 1]["section_times"][offset + i]
                self.section_labels[i].set_text(
                    "{:>3}:      {}".format(
                        offset+i+1, milliseconds_to_time_string(section_time - total_milliseconds))
                )
                total_milliseconds = section_time
            except IndexError:
                # This exception is expected if section time array length is less than
                # 'self.per_page'. clear the label
                self.section_labels[i].set_text("")

        try:
            lap_time = self.laps[lap_time_page- 1]["section_times"][-1]
            self.total_time.set_text(
                "{}".format(milliseconds_to_time_string(lap_time))
            )
        except IndexError:
            self.total_time.set_text("\' -- \" ---")

    def on_change_lap_time_pager(self):
        lap_time_page = self.lap_pager.get_value()
        if lap_time_page > 0:
            section_time_count = len(self.laps[lap_time_page- 1]["section_times"])
            npages = section_time_count // len(self.section_labels)
            if section_time_count % len(self.section_labels) != 0:
                npages = npages + 1

            self.section_time_pager.set_max_number(npages)
            self.show(lap_time_page)

    def on_change_section_time_pager(self):
        lap_time_page = self.lap_pager.get_value()
        section_time_page = self.section_time_pager.get_value()

        if lap_time_page > 0 and section_time_page > 0:
            lap_time_page = self.lap_pager.get_value()
            section_time_count = len(self.laps[lap_time_page- 1]["section_times"])
            npages = section_time_count // len(self.section_labels)
            if section_time_count % len(self.section_labels) != 0:
                npages = npages + 1
            self.section_time_pager.set_max_number(npages)
            self.show(lap_time_page, section_time_page)
