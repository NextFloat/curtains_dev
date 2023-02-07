import flet as ft
from .ContentContainer import ContentContainer

class SettingsMenu(ft.Column):

    def __init__(self):
        super().__init__()
        self.item_dict: dict = {}
        self.build_item('DEMO run on startup', 3)
        self.build_item('DEMO run as tray', 3)

    def build_item(self, name, type):
        item = SettingsItem(name,type)
        self.controls.append(item)
        self.item_dict[name] = item

class SettingsItem(ContentContainer):

    def __init__(self, name, action_type):
        title = ft.Text(value=name, color=ft.colors.WHITE54)
        super().__init__(title=title, icon=None, width=400, max_height=160, title_action=action_type)

        self.border = None
        self.padding = 0
        self.margin = 0
        self.height = 42
        #self.switch.on_change = lambda e:function(e)

def toggle_startup(e):
    print(e)

def toggle_tray(e):
    print(e)