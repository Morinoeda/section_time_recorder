import copy
import json
from ui.label import Label
from ui.button import Button, ButtonGroup
from ui.pager import HorizontalPager

class Checkpoint(object):
    def __init__(self, track_name, track_length, spline, enabled=True):
        self.track_name = track_name
        self.track_length = track_length
        self.spline = spline
        self.enabled = enabled

    def in_meter(self):
        return round(self.track_length * self.spline, 3)

    def __repr__(self):
        return "Checkpoint(track_name={},track_length={},spline={},enabled={})".format(
            self.track_name, self.track_length, self.spline, self.enabled
        )

    def __lt__(self, other):
        return self.spline < other.spline

    def __le__(self, other):
        return self.spline <= other.spline

    def __gt__(self, other):
        return self.spline > other.spline

    def __ge__(self, other):
        return self.spline >= other.spline

class File(object):
    checkpoint_key   = "checkpoints"
    track_name_key = "trackName"
    track_length_ley = "trackLength"
    track_spline_list_key = "splines"
    keys = [
        track_name_key,
        checkpoint_key,
    ]

    def __init__(self, filepath):
        self.filepath = filepath
        self.data = {File.checkpoint_key: []}

    def load(self):
        self.data = json.load(open(self.filepath, "r", encoding="utf-8"))

    def save(self):
        json.dump(self.data, open(self.filepath, "w", encoding="utf-8"))

    def get_checkpoints(self, track_name):
        checkpoints = []
        for item in self.data[File.checkpoint_key]:
            if track_name == item[File.track_name_key]:
                for spline in item[File.track_spline_list_key]:
                    checkpoints.append(Checkpoint(
                        track_name=track_name,
                        track_length=item[File.track_length_ley],
                        spline=spline
                    ))

        return checkpoints

    def set_checkpoints(self, checkpoints):
        track_length = checkpoints[0].track_length
        track_name  = checkpoints[0].track_name
        splines = [c.spline for c in checkpoints]
        for i, item in enumerate(self.data[File.checkpoint_key]):
            if track_name == item[File.track_name_key]:
                self.data[File.checkpoint_key][i][File.track_spline_list_key] = splines
                self.data[File.checkpoint_key][i][File.track_length_ley] = track_length

        self.data[File.checkpoint_key].append({
            File.track_name_key: track_name,
            File.track_length_ley: track_length,
            File.track_spline_list_key: splines,
        })

class View(object):
    def __init__(self,
                window,
                x,
                y,
                width,
                height,
                ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.spline_title_label = Label(
            window=window,
            x=x,
            y=y,
            width=width/3,
            height=20,
            text="Spline"
        )

        self.spline_label = Label(
            window=window,
            x=x+40,
            y=y+40,
            width=width*2/3,
            height=20,
        )

    def set(self, checkpoint: Checkpoint):
        self.spline_label.set_text("{} m / {} m".format(
            round(checkpoint.in_meter(), 2), round(checkpoint.track_length, 2)))

    def set_visible(self, visible):
        self.spline_title_label.set_visible(visible)
        self.spline_label.set_visible(visible)

class Control(object):
    tracking_mode = "Tracking"
    recording_mode = "Recording"
    disabled_mode  = "Disable"

    def __init__(self,
                window,
                x,
                y,
                width,
                height,
                on_change_mode=None,
                on_add=None,
                on_remove=None,
                on_save=None,
                on_load=None
                ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.padding = 10

        # main controls
        self.control_title_label = Label(
            window=window,
            x=x+self.padding,
            y=y,
            width=width,
            height=30,
            text="Mode switching",
            font_align="center"
        )
        self.control_title_label.set_custom_font(bold=True)

        self.mode_buttons = ButtonGroup(
            window=window,
            x=x+self.padding,
            y=self.control_title_label.y + self.control_title_label.height,
            width=self.width - self.padding*2,
            height=30,
            labels=[Control.disabled_mode, Control.tracking_mode, Control.recording_mode],
            selected=Control.disabled_mode,
            on_click=on_change_mode
        )

        self.recording_control_label = Label(
            window=window,
            x=x+self.padding,
            y=self.mode_buttons.y + self.mode_buttons.height + 10,
            width=width,
            height=30,
            text="Recording",
            font_align="center"
        )
        self.recording_control_label.set_custom_font(bold=True)

        # add checkpoint button
        self.add_button = Button(
            window=window,
            x=x+self.padding,
            y=self.recording_control_label.y + self.recording_control_label.height,
            width=(self.width - self.padding*2)/4,
            height=30,
            label="Mark",
            on_click=on_add
        )

        # remove checkpoint button
        self.remove_button = Button(
            window=window,
            x=x+self.padding + (width- self.padding *2)/4,
            y=self.recording_control_label.y + self.recording_control_label.height,
            width=(width - self.padding*2)/4,
            height=30,
            label="Remove",
            on_click=on_remove
        )

        # save checkpoint button
        self.save_button = Button(
            window=window,
            x=x+self.padding+(width - self.padding*2)/2,
            y=self.recording_control_label.y + self.recording_control_label.height,
            width=(width - self.padding*2)/4,
            height=30,
            label="Save",
            on_click=on_save,
        )

        # load checkpoint button
        self.load_button = Button(
            window=window,
            x=x+self.padding+(width - self.padding*2)*3/4,
            y=self.recording_control_label.y + self.recording_control_label.height,
            width=(width - self.padding*2)/4,
            height=30,
            label="Load",
            on_click=on_load
        )

        self.checkpoint_control_label = Label(
            window=window,
            x=x+self.padding,
            y=self.add_button.y + self.add_button.height + 10,
            width=width,
            height=30,
            text="Checkpoint View",
            font_align="center"
        )
        self.checkpoint_control_label.set_custom_font(bold=True)

        self.checkpoint_view = View(
            window,
            x=x+self.padding,
            y=self.checkpoint_control_label.y + self.checkpoint_control_label.height,
            width=width - self.padding*2,
            height=100,
        )
        self.checkpoint_view.set_visible(False)

        self.pager = HorizontalPager(
            window=window,
            x=x+self.padding + (width - self.padding*2)*1/3,
            y=self.checkpoint_view.y + self.checkpoint_view.height + 10,
            width=(self.width - self.padding*2)*1/3,
            height=30,
            on_change=self.on_change_checkpoint
        )
        self.pager.set_visible(False)

        self.checkpoints = []

    def set_visible(self, visible):
        self.control_title_label.set_visible(visible)
        self.mode_buttons.set_visible(visible)
        self.recording_control_label.set_visible(visible)
        self.add_button.set_visible(visible)
        self.remove_button.set_visible(visible)
        self.save_button.set_visible(visible)
        self.load_button.set_visible(visible)
        self.checkpoint_control_label.set_visible(visible)
        self.pager.set_visible(visible)

        if self.pager.get_value() == 0:
            self.checkpoint_view.set_visible(False)
            self.pager.set_visible(False)

    def set_checkpoint_view(self):
        page_number = self.pager.get_value()
        if page_number > 0:
            self.checkpoint_view.set(self.checkpoints[page_number-1])
            self.checkpoint_view.set_visible(True)
            self.pager.set_visible(True)
        else:
            self.checkpoint_view.set_visible(False)
            self.pager.set_visible(False)

    def set_checkpoints(self, checkpoints):
        self.checkpoints.clear()
        for checkpoint in checkpoints:
            self.checkpoints.append(copy.deepcopy(checkpoint))

        self.pager.set_max_number(len(self.checkpoints))
        self.set_checkpoint_view()

    def get_selected_checkpoint(self):
        return self.pager.get_value() - 1

    def get_selected_mode(self):
        return self.mode_buttons.get_selected()

    def set_mode(self, mode):
        self.mode_buttons.set_selected(mode)

    def on_change_checkpoint(self):
        pass
