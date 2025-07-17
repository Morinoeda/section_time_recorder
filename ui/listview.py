from ui.button import Button
from ui.div import Div

class ListItem(Button):
    def __init__(self, window, x, y, width, height, label="", on_click=None):
        super().__init__(window, x, y, width, height, label, None)

        self.callback = on_click
        self.draw_boarder(False)
        self.draw_background(False)
        self.set_font_alignment("left")
        self.set_selected(False)

    def __eq__(self, value):
        return self.label == value.label

    def set_selected(self, enable):
        self.set_background_opacity(1.0 if enable else 0)

    def on_click(self, *args):
        if self.callback is not None:
            self.callback(self.label)

class ListView(object):
    def __init__(self,
                window,
                x,
                y,
                width,
                item_height=20,
                item_list=None,
                selected=None,
                draw_item_boarder=False,
                on_select=None):
        self.x = x
        self.y = y
        self.window = window
        self.width = width
        self.item_list = item_list
        self.callback = on_select
        self.draw_item_boarder = draw_item_boarder

        self.item_height = item_height
        self.selected = selected

        self.list_items = []
        if self.item_list is not None:
            # For putting items front of the background, rendering background first
            self.background = Div(
                window=window,
                x=x,
                y=y,
                width=width,
                height=item_height*len(self.item_list)
            )

            for i, item in enumerate(self.item_list):
                self.list_items.append(ListItem(
                    window=self.window,
                    x=x,
                    y=y + self.item_height*i,
                    width=width,
                    height=self.item_height,
                    label=item,
                    on_click=self.on_select
                ))
                if self.list_items[i].label == self.selected:
                    self.list_items[i].set_selected(True)

            if len(self.list_items) > 0 and self.selected is None:
                self.list_items[0].set_selected(True)
                self.selected = self.list_items[0].label

    def __len__(self):
        return len(self.list_items)

    def set_visible(self, visible):
        self.background.set_visible(visible)
        for item in self.list_items:
            item.set_visible(visible)

    def get_selected(self):
        return self.selected

    def on_select(self, label):
        # Disable highlight
        for item in self.list_items:
            if label == item.label:
                self.selected = label
                item.set_selected(True)
            else:
                item.set_selected(False)

        if self.callback is not None:
            self.callback(label)
