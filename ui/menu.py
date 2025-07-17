from ui.listview import ListView

class VerticalMenu(ListView):
    def __init__(self, window, x, y, width, item_height=20, item_list=None,
                 selected=None, draw_item_boarder=True, on_select=None):
        super().__init__(window, x, y, width, item_height, item_list,
                         selected, draw_item_boarder, on_select)
