import os
import os.path
import inspect
from queue import Queue
import platform
import sys
import copy
import ac # pylint: disable=E0401
import acsys # pylint: disable=E0401
from checkpoint import Checkpoint, Control as CheckpointControl, File as CheckpointFile
from control import ControlApp
from laps import LaptimeApp
from history import HistoryApp

# ctypes library is different for 32 and 64 bits respectively
if platform.architecture()[0] == "64bit":
    DLL_FOLDER = "stdlib64"
else:
    DLL_FOLDER = "stdlib"
cwd = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(cwd, DLL_FOLDER))
os.environ['PATH'] = os.environ['PATH'] + ";."

from third_party.sim_info import SimInfo # pylint: disable=C0413

APP_VERSION = "1.0"
APP_NAME = "Section Time"
APP_DIR_NAME = "section_time_recorder"
CHECKPOINT_FILE_PATH= os.path.join(
    os.getcwd(),
    "apps",
    "python",
    APP_DIR_NAME,
    "checkpoint.json"
)
CAR_ID = 0
CAR_NAME = ac.getCarName(CAR_ID)
TRACK_NAME = ac.getTrackName(CAR_ID)
TRACK_LAYOUT = ac.getTrackConfiguration(CAR_ID)
TRACK_LENGTH = ac.getTrackLength(CAR_ID)

MESSAGES = {
    "no_checkpoint": "No checkpoint.\nOne or more checkpoint require.\nClick 'Recording' to start."
}


class SectionRecord(object):
    def __init__(self, checkpoint: Checkpoint):
        self.checkpoint = checkpoint
        self.is_passed = False
        self.milliseconds = None

class Context(object):
    def __init__(self):
        self.eventq = Queue()
        self.state = None
        self.scoreboard = []
        self.history = {}
        self.siminfo = SimInfo()

        self.spline = 0
        self.lap_count = 0
        self.lap_time = 0.0

        self.control_app = ControlApp(
            name="{} Setting".format(APP_NAME),
            on_add_checkpoint=lambda: self.handle_ui_event("on_add"),
            on_remove_checkpoint=lambda: self.handle_ui_event("on_remove"),
            on_save_checkpoint=lambda: self.handle_ui_event("on_save"),
            on_load_checkpoint=lambda: self.handle_ui_event("on_load"),
            on_change_mode=lambda: self.handle_ui_event("on_change_mode")
        )

        self.lap_time_app = LaptimeApp(
            name="{} Laps".format(APP_NAME)
        )
        self.history_app  = HistoryApp(
            name="{} History".format(APP_NAME)
        )

    def change_checkpoints(self, checkpoints):
        checkpoints.sort()
        self.scoreboard.clear()
        for c in checkpoints:
            self.scoreboard.append(SectionRecord(c))

    def get_current_checkpoint(self):
        record = next(filter(lambda x: not x.is_passed, self.scoreboard), None)
        if record is None:
            return None

        return record.checkpoint

    def pass_current_checkpoint(self, milliseconds):
        record = next(filter(lambda x: not x.is_passed, self.scoreboard), None)
        if record is not None:
            record.milliseconds = milliseconds
            record.is_passed = True
            self.lap_time_app.append_section_time(milliseconds)

    def clear_scoreboard(self):
        for i, _ in enumerate(self.scoreboard):
            self.scoreboard[i].is_passed = False
            self.scoreboard[i].milliseconds = 0

    def clear_history(self):
        self.history.clear()

    def next_lap(self):
        lap_time = ac.getCarState(CAR_ID, acsys.CS.LastLap)
        self.history[self.lap_count] = [ r.milliseconds for r in self.scoreboard ] + [lap_time]
        self.history_app.append(self.lap_count, self.history[self.lap_count])
        self.lap_time_app.clear()
        self.clear_scoreboard()

    def process_simulation_event(self):
        if self.state is None:
            self.state = DisabledState(self)

        while not self.eventq.empty():
            event = self.eventq.get()
            for name, handler in inspect.getmembers(self.state, inspect.ismethod):
                if event == name:
                    self.state = handler(self, event)

        lap_time = ac.getCarState(CAR_ID, acsys.CS.LapTime)
        lap_count = ac.getCarState(CAR_ID, acsys.CS.LapCount)
        spline = round(ac.getCarState(CAR_ID, acsys.CS.NormalizedSplinePosition), 9)

        self.state = self.state.process(
            context=self,
            lap_time=lap_time,
            lap_count=lap_count,
            spline=spline
        )

        self.lap_count = lap_count
        self.lap_time = lap_time
        self.spline   = spline

        self.lap_time_app.set_lap_time(lap_time)

    def handle_ui_event(self, event):
        self.eventq.put(event)

class StateBase(object):
    def __init__(self, context):
        pass
    def __eq__(self, value):
        return str(self) == str(value)
    def process(self, context, lap_time, lap_count, spline):
        return self
    def on_add(self, context, event):
        return self
    def on_remove(self, context, event):
        return self
    def on_change_mode(self, context, event):
        return self
    def on_save(self, context, event):
        return self
    def on_load(self, context, event):
        return self

class DisabledState(StateBase):
    def __init__(self, context):
        super().__init__(context)
        context.control_app.checkpoint_control.set_mode(CheckpointControl.disabled_mode)

    def __str__(self):
        return "DisableState"

    def on_change_mode(self, context, event):
        mode = context.control_app.checkpoint_control.get_selected_mode()
        if mode == CheckpointControl.tracking_mode:
            if len(context.scoreboard) >0:
                context.control_app.message_label.set_text("")
                return StartWaitState(context)
            else:
                context.control_app.message_label.set_text(MESSAGES["no_checkpoint"])
                return self
        elif mode == CheckpointControl.recording_mode:
            context.control_app.message_label.set_text("")
            return RecordingState(context)
        else:
            context.control_app.message_label.set_text(MESSAGES["no_checkpoint"])
            return self

class RecordingState(StateBase):
    def __init__(self, context):
        super().__init__(context)
        self.checkpoints = [r.checkpoint for r in context.scoreboard]
        context.control_app.checkpoint_control.set_checkpoints(self.checkpoints)
        context.control_app.checkpoint_control.set_mode(CheckpointControl.recording_mode)

    def __str__(self):
        return "RecordingState"

    def process(self, context, lap_time, lap_count, spline):
        if context.siminfo.graphics.status == 1:
            return ReplayState(context)
        else:
            return self

    def on_change_mode(self, context, event):
        mode = context.control_app.checkpoint_control.get_selected_mode()
        if mode == CheckpointControl.tracking_mode:
            if len(self.checkpoints) >0:
                context.control_app.message_label.set_text("")
                context.change_checkpoints(self.checkpoints)
                return StartWaitState(context)
            else:
                context.control_app.message_label.set_text(MESSAGES["no_checkpoint"])
                return self
        elif mode == CheckpointControl.disabled_mode:
            context.control_app.checkpoint_control.set_checkpoints([])
            return DisabledState(context)
        else:
            return self

    def on_add(self, context, event):
        if ac.isCarInPitlane(CAR_ID) != 1:
            spline = ac.getCarState(CAR_ID, acsys.CS.NormalizedSplinePosition)
            checkpoint = Checkpoint(
                track_name=TRACK_NAME, track_length=TRACK_LENGTH, spline=spline
            )
            self.checkpoints.append(checkpoint)
            self.checkpoints.sort()
            context.control_app.checkpoint_control.set_checkpoints(self.checkpoints)
        return self

    def on_remove(self, context, event):
        index = context.control_app.checkpoint_control.get_selected_checkpoint()
        try:
            self.checkpoints.pop(index)
            self.checkpoints.sort()
            context.control_app.checkpoint_control.set_checkpoints(self.checkpoints)
        except IndexError:
            ac.log("index error index={}".format(index))
        return self

    def on_save(self, context, event):
        ac.log("on save checkpoints {}".format(self.checkpoints))
        if len(self.checkpoints) > 0:
            checkpoint_file = CheckpointFile(CHECKPOINT_FILE_PATH)
            checkpoint_file.set_checkpoints(self.checkpoints)
            try:
                checkpoint_file.save()
            except Exception as e: # pylint: disable=W0718
                ac.log("error on saving checkpoint to {}".format(CHECKPOINT_FILE_PATH))
                ac.log("{}".format(e))
        else:
            context.control_app.message_label.set_text(MESSAGES["no_checkpoint"])

        return self

    def on_load(self, context, event):
        self.checkpoints.clear()
        checkpoint_file = CheckpointFile(CHECKPOINT_FILE_PATH)
        try:
            checkpoint_file.load()
        except Exception as e: # pylint: disable=W0718
            ac.log("error on loading checkpoint from {}".format(CHECKPOINT_FILE_PATH))
            ac.log("{}".format(e))

        for c in checkpoint_file.get_checkpoints(TRACK_NAME):
            self.checkpoints.append(c)

        context.control_app.checkpoint_control.set_checkpoints(self.checkpoints)
        return self

class TrackingStateBase(StateBase):
    def on_change_mode(self, context, event):
        mode = context.control_app.checkpoint_control.get_selected_mode()
        if mode == CheckpointControl.disabled_mode:
            return DisabledState(context)
        elif mode == CheckpointControl.recording_mode:
            return RecordingState(context)
        else:
            return self

class StartWaitState(TrackingStateBase):
    def __init__(self, context):
        context.control_app.checkpoint_control.set_mode(CheckpointControl.tracking_mode)
        context.clear_scoreboard()
    def __str__(self):
        return "StartWait"
    def process(self, context, lap_time, lap_count, spline):
        if context.siminfo.graphics.status == 1:
            return ReplayState(context)

        if 0 < lap_time:
            return WaitSplineErrorPassedState(context)
        return self

class WaitSplineErrorPassedState(TrackingStateBase):
    def __str__(self):
        return "Wait spline error"

    def process(self, context, lap_time, lap_count, spline):
        if context.siminfo.graphics.status == 1:
            return ReplayState(context)

        if context.lap_count > lap_count:
            return StartWaitState(context)

        if spline < 0.9:
            return MeasurementState(context)

        return self

class MeasurementState(TrackingStateBase):
    def __str__(self):
        return "Measuring"

    def process(self, context, lap_time, lap_count, spline):
        if context.siminfo.graphics.status == 1:
            return ReplayState(context)

        if lap_time < context.lap_time:
            return StartWaitState(context)

        if context.lap_count > lap_count:
            return StartWaitState(context)

        checkpoint = context.get_current_checkpoint()
        if checkpoint is None:
            return WaitFinishState(context)

        if checkpoint.spline <= spline:
            context.pass_current_checkpoint(lap_time)

        return self

class WaitFinishState(TrackingStateBase):
    def __str__(self):
        return "Wait for finish"

    def process(self, context, lap_time, lap_count, spline):
        if context.siminfo.graphics.status == 1:
            return ReplayState(context)

        if lap_time < context.lap_time:
            if context.lap_count < lap_count:
                context.next_lap()
            return StartWaitState(context)
        return self

class ReplayState(StateBase):
    def __init__(self, context):
        super().__init__(context)
        self.previous_state = context.state
        self.scoreboard     = copy.deepcopy(context.scoreboard)
        self.history        = copy.deepcopy(context.history)

    def __str__(self):
        return "Replay"

    def process(self, context, lap_time, lap_count, spline):
        ac.log("In replay mode")
        if context.siminfo.graphics.status != 1:
            return self.previous_state

        # stil in replay mode
        return self

ctx = Context()

def acMain(ac_version): # pylint: disable=C0103
    """Main function for Assetto Corsa Mod
    """
    return APP_NAME + " " + APP_VERSION

def acUpdate(delta_time): # pylint: disable=C0103
    """Update function for Assetto Corsa Mod
    """
    ctx.process_simulation_event()
