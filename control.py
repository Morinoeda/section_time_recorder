from ui.window import Window
from ui.menu import VerticalMenu
from ui.label import Label
from checkpoint import Control as CheckpointControl

class ControlApp(Window):
    menu_label_checkpoint = "Checkpoints"
    menu_lable_setting    = "Setting"
    menu_label_help       = "Help"

    def __init__(self, name, width=400, height=500,
                 on_change_mode=None, on_add_checkpoint=None, on_remove_checkpoint=None,
                 on_save_checkpoint=None, on_load_checkpoint=None):
        super().__init__(name, width, height)

        self.menu_list = VerticalMenu(
            window=self.window,
            x=0,
            y=40,
            width=width/5,
            item_height=30,
            item_list=[
                ControlApp.menu_label_checkpoint,
                ControlApp.menu_lable_setting,
                ControlApp.menu_label_help,
            ],
            selected=ControlApp.menu_label_checkpoint,
            on_select=self.on_menu_item_selected
        )

        # Main controls
        self.checkpoint_control = CheckpointControl(
            window=self.window,
            x=self.menu_list.width + 20,
            y=40,
            width=width * 3/4,
            height=height * 4/5,
            on_add=on_add_checkpoint,
            on_remove=on_remove_checkpoint,
            on_save=on_save_checkpoint,
            on_load=on_load_checkpoint,
            on_change_mode=on_change_mode
        )

        self.help_label = Label(
            window=self.window,
            x=self.menu_list.width + 20,
            y=40,
            width=width * 3/4,
            height=height * 4/5
        )

        self.message_label = Label(
            window=self.window,
            x=self.menu_list.width + 20,
            y=self.checkpoint_control.y + self.checkpoint_control.height,
            width=width * 3/4,
            height=height * 1/5,
        )

    def on_menu_item_selected(self, menu):
        if ControlApp.menu_label_checkpoint == menu:
            self.checkpoint_control.set_visible(True)
            self.help_label.set_visible(False)
        elif ControlApp.menu_lable_setting == menu:
            self.checkpoint_control.set_visible(False)
            self.help_label.set_visible(False)
        elif ControlApp.menu_label_help == menu:
            self.checkpoint_control.set_visible(False)
            self.help_label.set_visible(True)
