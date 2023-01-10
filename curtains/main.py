import logging
import time
import atexit
import threading

import flet as ft

import curtains
import database as db

# CONSTANTS
# WINDOW_WIDTH = 700
ROW_HEIGHT = 52

# COLORS
COLOR_BG = '#111112'
COLOR_SECONDARY = '#1B1B1B'
COLOR_PRIMARY = '#222222'
COLOR_TRANSPARENT = ft.colors.TRANSPARENT


# TODO: reduce try/except; catch Exceptions by logging; fix with if conditions
# TODO: hide everything mode: if new pid = hide(pid) [easy]
# TODO: autostart on login: create Task [should be easy]
# TODO: run as tray icon, not in taskbar: https://github.com/ndonkoHenri/Flet-as-System-Tray-Icon [should be easy]
# TODO: check if hidden = get windows to foreground, take screenshot, check if windowregion is black [easy]
# TODO: windowmanager, autorename windowtitles (rules? e.g. browser titles) #toppings
# TODO: add tooltips
# fixme: find a way to unhide only windows that were visible before. unhiding some apps results in unclickable windwos
#       that were never visible, need to tinker with C++ DLL [hard]


class Window:
    def __init__(self, hwnd, pid, left=None, top=None, right=None, bottom=None):
        self.hwnd: int = hwnd
        self.title: str | None = None
        self.pid: int = pid
        self.left: int | None = left
        self.top: int | None = top
        self.right: int | None = right
        self.bottom: int | None = bottom

    # overloading equals: ==, in
    def __eq__(self, val):
        if val == self.hwnd:
            return True


class Process:
    def __init__(self, pid):
        self.pid: int = pid
        self.name: str | None = None
        self.path: str | None = None
        self.icon: str | None = None
        self.user: str | None = None
        self.windows: list[Window] = []
        self.hidden: bool = False

    # overloading equals: ==, in
    def __eq__(self, val):
        if val == self.pid:
            return True


class ProcessTable(ft.DataTable):
    def __init__(self, ):
        super().__init__()

        self.locked = db.read_table()  # {process_path:{hidden:bool,icon:b64_str}

        self.height: int = 80
        self.rows_dict: dict = {}
        self.p_dict: dict = {}
        self.update_pids_hwnds()
        self.columns = [
            ft.DataColumn(ft.Text("")),
            ft.DataColumn(ft.Text("pid"), numeric=True, on_sort=self.sort_rows),
            ft.DataColumn(ft.Text("process"), on_sort=self.sort_rows),
            ft.DataColumn(ft.Text("windows"), on_sort=self.sort_rows),
            ft.DataColumn(ft.Text('hidden'), on_sort=self.sort_rows),
            ft.DataColumn(ft.Text('remember'), on_sort=self.sort_rows)
        ]
        self.data_row_color = COLOR_SECONDARY
        self.heading_row_color = COLOR_SECONDARY
        self.column_spacing: int = 5
        self.width = curtains.return_screensize()[0] / 3
        self.data_row_height: int = 48
        self.border = ft.border.all(14, COLOR_SECONDARY)
        self.border_radius = ft.border_radius.all(15)

        for p in self.p_dict:
            row = self.build_new_row(self.p_dict[p].icon, p, self.p_dict[p].name, len(self.p_dict[p].windows),
                                     self.p_dict[p].hidden)
            self.rows.append(row)

    def build_new_row(self, icon, pid, pname, wcount, hidden):
        if not isinstance(icon, str):
            icon_cell = ft.DataCell(
                ft.CircleAvatar(content=ft.Text(pname[0:1].title(), size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE), radius=10,
                                bgcolor=ft.colors.INVERSE_PRIMARY))
        else:
            icon_cell = ft.DataCell(ft.Image(src_base64=icon, width=20, height=20,
                                             fit=ft.ImageFit.CONTAIN, ))

        lock_cell = ft.IconButton(
            icon=ft.icons.LOCK_OPEN,
            icon_color=ft.colors.INVERSE_PRIMARY,
            icon_size=16,
            on_click=lambda e, p=self.p_dict[pid]: self.lock(e, p)
        )

        hidden_cell = ft.Checkbox(
            value=hidden,
            fill_color=ft.colors.INVERSE_PRIMARY,
            on_change=lambda e, p=self.p_dict[pid]: self.toggle_hidden(e, p)
        )

        row = ft.DataRow(
            [icon_cell,
             ft.DataCell(ft.Text(pid)),
             ft.DataCell(ft.Text(pname)),
             ft.DataCell(ft.Text(wcount)),
             ft.DataCell(hidden_cell),
             ft.DataCell(lock_cell)
             ]
        )
        self.rows_dict[pid] = row

        if hidden:
             self.toggle_hidden('true', self.p_dict[pid])
             self.lock(lock_cell, self.p_dict[pid])

        self.height += self.data_row_height

        return row

    def sort_rows(self, e):
        def cell_value(row):
            content = row.cells[col_index].content
            if hasattr(content, 'value'):
                value = content.value
            else:
                value = content.icon
            return (value)

        col_index = e.column_index
        order = e.ascending
        self.sort_column_index = col_index
        # self.rows.sort(key=lambda x: x.cells[col_index].content.value, reverse=order)
        self.rows.sort(key=cell_value, reverse=order)
        self.sort_ascending = not self.sort_ascending
        self.update()

    def toggle_hidden(self, e, process):
        if type(e) == ft.control_event.ControlEvent:  # check if in construction or page loaded
            e = e.data
        if e == 'true':
            process.hidden = True
            for i in self.rows_dict[process.pid].cells[1:4]:
                i.content.color = ft.colors.WHITE24
            h_thread = threading.Thread(target=curtains.hide_windows, args=(process.pid,))
            h_thread.start()
            #curtains.hide_windows(process.pid)

        if e == 'false':
            process.hidden = False
            for i in self.rows_dict[process.pid].cells[1:4]:
                i.content.color = ft.colors.WHITE
            uh_thread = threading.Thread(target=curtains.unhide_windows, args=(process.pid,))
            uh_thread.start()
            #curtains.unhide_windows(process.pid)

        if process.path in self.locked:
            db.update_hidden(process.path, process.hidden)

    def lock(self, e, p):
        if type(e) == ft.control_event.ControlEvent:
            e = e.control
        if e.icon == 'lock_open':
            e.icon = 'lock'
            e.icon_color = ft.colors.AMBER
            if p.path not in self.locked:
                db.add_row(p.path, p.hidden, p.icon)
                self.locked[p.path] = {'hidden': p.hidden, 'icon': p.icon}
            # rows_dict[p.pid].color = ft.colors.AMBER

        else:
            e.icon = 'lock_open'
            e.icon_color = ft.colors.INVERSE_PRIMARY
            self.rows_dict[p.pid].color = COLOR_SECONDARY
            db.delete_row(p.path)
            self.locked.pop(p.path)

    def update_pids_hwnds(self):
        pid_set = set()
        hwnd_set = set(curtains.all_hwnds())
        ignore_pids = [0, 4]  # 0=system idle, 4 = kernel
        for hwnd in hwnd_set:
            found_pid = curtains.pid_of_hwnd(hwnd)
            if found_pid not in ignore_pids:
                pid_set.add(found_pid)

        for pid in pid_set:
            if pid not in self.p_dict:
                p = Process(pid)
                for hwnd in hwnd_set:
                    if curtains.pid_of_hwnd(hwnd) == pid and hwnd not in p.windows:
                        p.windows.append(Window(hwnd, pid))

                try:
                    p.name = curtains.process_name_of_pid(p.pid)
                except Exception as Argument:
                    logging.exception(f'{Argument}\nprocessname for PID:{p.pid} not found.')
                    continue

                p.path = curtains.executable_path(p.name, p.pid)

                if p.path in self.locked:
                    p.icon = self.locked[p.path]['icon']
                    p.hidden = self.locked[p.path]['hidden']

                if p.icon is None:
                    img_icon = curtains.extract_icon(p.path, p.windows[0].hwnd)
                    if hasattr(img_icon, 'convert'):
                        p.icon = curtains.image2base64(img_icon)
                    else:
                        p.icon = None

                self.p_dict[pid] = p
            else:
                for hwnd in hwnd_set:
                    if curtains.pid_of_hwnd(hwnd) == pid and hwnd not in self.p_dict[pid].windows:
                        self.p_dict[pid].windows.append(Window(hwnd, pid))

        # remove dead processes and windows
        for process_pid in self.p_dict.copy():
            if process_pid not in pid_set:
                self.p_dict.pop(process_pid)
                continue

            else:
                for window in self.p_dict[process_pid].windows:
                    if window.hwnd not in hwnd_set:

                        self.p_dict[process_pid].windows.remove(window)

    def update_data(self):
        self.update_pids_hwnds()

        for r in self.rows:
            row_pid = int(r.cells[1].content.value)

            # check if shown process does not exist anymore
            if self.p_dict.get(row_pid) is None:
                self.rows_dict.pop(row_pid)
                self.rows.remove(r)
                self.height -= self.data_row_height

            # check if windowcount differs
            elif int(r.cells[3].content.value) != len(self.p_dict[row_pid].windows):
                if int(r.cells[3].content.value) < len(self.p_dict[row_pid].windows):
                    if self.p_dict[row_pid].hidden is True:
                        curtains.hide_windows(row_pid)
                r.cells[3].content.value = len(self.p_dict[row_pid].windows)
                self.update()

        # else after iterator = finally/do after last iteration
        else:
            for p in self.p_dict:
                if p not in self.rows_dict:
                    row = self.build_new_row(self.p_dict[p].icon, p, self.p_dict[p].name, len(self.p_dict[p].windows),
                                             self.p_dict[p].hidden)
                    self.rows.append(row)


class ScreenshotContainer(ft.Container):

    def __init__(self):
        super().__init__()
        self.update_delay = 0.5  # seconds between screenshots
        self.preview_switch = ft.Switch(value=False, active_color=ft.colors.INVERSE_PRIMARY,
                                        on_change=lambda e: self.toggle_preview_stack(e))
        self.title = ft.Text(value='preview', weight=ft.FontWeight.BOLD)
        self.title_row = ft.Row([self.title, self.preview_switch],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self.text_row_1 = ft.Row([ft.Text(value='screenshot interval:'), ScaleWidget(self)],
                                 alignment=ft.MainAxisAlignment.START)
        self.screenshot = ft.Image(src_base64=curtains.image2base64(curtains.take_screenshot()),
                                   fit=ft.ImageFit.FILL)
        self.screenshot_time = time.time()
        self.content = ft.Column([self.title_row, self.text_row_1, self.screenshot])
        self.width = (curtains.return_screensize()[0] / 4)
        self.height = (curtains.return_screensize()[1] / 2.7)
        self.bgcolor = COLOR_SECONDARY
        self.border = ft.border.all(14, COLOR_SECONDARY)
        self.border_radius = ft.border_radius.all(15)
        self.toggle_preview_stack(str(self.preview_switch.value).lower())

    def update_preview(self):
        if self.preview_switch.value is True and (time.time() - self.screenshot_time) >= self.update_delay:
            screenshot = curtains.take_screenshot()
            if screenshot:
                self.screenshot.src_base64 = curtains.image2base64(screenshot)
                self.screenshot_time = time.time()
            else:
                print('ERROR: could not take screenshot')

    def toggle_preview_stack(self, e):
        if type(e) == ft.control_event.ControlEvent:
            e = e.data
        if e == 'true':
            # self.content.controls[1] = self.screenshot
            self.screenshot.opacity = 1
            # self.screenshot.visible = True
            # self.height = (curtains.return_screensize()[1] / 3)
        if e == 'false':
            # self.content.controls[1] = self.stack
            self.screenshot.opacity = 0.25
            # self.screenshot.visible = False
            # self.height = 80


class ScaleWidget(ft.Container):
    def __init__(self, target):
        super().__init__()
        decrease = ft.IconButton(icon=ft.icons.ARROW_BACK_IOS_ROUNDED, scale=1,
                                 on_click=lambda e, t=target: self.decrease(e, t),
                                 icon_color=ft.colors.INVERSE_PRIMARY)
        increase = ft.IconButton(
            icon=ft.icons.ARROW_FORWARD_IOS_ROUNDED,
            scale=1,
            on_click=lambda e, t=target: self.increase(e, t),
            icon_color=ft.colors.INVERSE_PRIMARY,
            style=ft.ButtonStyle(shape=ft.StadiumBorder())
        )
        target_string = str(target.update_delay)
        self.number = ft.Text(value=target_string)
        self.content = ft.Row([decrease, self.number, increase], alignment=ft.MainAxisAlignment.CENTER, tight=True,
                              spacing=0)

    def decrease(self, e, t):
        t.update_delay = round(t.update_delay - 0.1, 1)
        self.number.value = str(t.update_delay)

    def increase(self, e, t):
        t.update_delay = round(t.update_delay + 0.1, 1)
        self.number.value = str(t.update_delay)


class Navbar(ft.AppBar):
    def __init__(self, p_table):
        super().__init__()

        self.searchbox = ft.TextField(
            label="search process",
            border=ft.InputBorder.NONE,
            filled=True,
            multiline=False,
            text_size=12,
            prefix_icon=ft.icons.SEARCH,
            on_change=lambda e, datatable=p_table: self.search_proc(e, datatable)
        )
        self.title = ft.Row(spacing=13, height=ROW_HEIGHT,
                            controls=[ft.Image(src='/assets/curtains_32.png', fit=ft.ImageFit.SCALE_DOWN),
                                      self.searchbox])
        self.leading_width = 40
        self.center_title = False
        self.toolbar_height = ROW_HEIGHT
        self.bgcolor = COLOR_SECONDARY
        self.actions = [
            ft.Icon(ft.icons.DESKTOP_ACCESS_DISABLED, color=ft.colors.INVERSE_PRIMARY),
            ft.IconButton(ft.icons.SETTINGS),
            ft.PopupMenuButton(
                items=[
                    # ft.PopupMenuItem(text="Item 1"),
                    # ft.PopupMenuItem(),  # divider
                    # ft.PopupMenuItem(text="Checked item", checked=False),
                ]
            ),
        ]

    def search_proc(self, e, p_table):

        def keyword_search(r):
            p_name = r.cells[2].content.value.lower()
            if p_name.startswith(e.data.lower()):
                result = "0" + p_name
                r.color = ft.colors.WHITE10
            else:
                result = p_name
                r.color = COLOR_SECONDARY
            return result

        p_table.rows.sort(key=keyword_search)
        if e.data == '':
            for row in p_table.rows:
                row.color = COLOR_SECONDARY
        p_table.update()


if __name__ == "__main__":
    def main(page: ft.Page):
        def calc_window_height():
            nav_height = page.appbar.toolbar_height
            additional_space = 8
            if screenshot_container.height > process_table.height:
                page.window_height = nav_height * 2 + screenshot_container.height + additional_space
            else:
                page.window_height = nav_height * 2 + process_table.height + additional_space


        page.bgcolor = COLOR_BG
        page.window_center()
        page.window_width = (curtains.return_screensize()[0] / 3) * 1.82
        # page.scroll = ft.ScrollMode.AUTO
        page.window_frameless = False
        page.window_title_bar_hidden = False
        page.window_title_bar_buttons_hidden = False
        page.window_resizable = True
        page.title = "Curtains"

        update_interval = 1 / 65  # frequency should be higher than FPS of screensharing + time needed to hide
        process_table = ProcessTable()
        page.window_min_width = process_table.width + (process_table.column_spacing * len(process_table.columns)) + 5
        page.theme_mode = ft.ThemeMode.DARK
        screenshot_container = ScreenshotContainer()
        content_col_2 = ft.Column([screenshot_container])
        content_col_1 = ft.Column([process_table], scroll=ft.ScrollMode.AUTO)

        content_row = ft.Row([content_col_1, content_col_2], vertical_alignment=ft.CrossAxisAlignment.START)
        page.add(content_row)
        page.appbar = Navbar(process_table)

        # for p in process_table.p_dict: # hide remembered processes
        #     if process_table.p_dict[p].path in process_table.locked:
        #         process_table.toggle_hidden('true', process_table.p_dict[p])

        while True:  # main loop
            process_table.update_data()
            calc_window_height()
            screenshot_container.update_preview()
            page.update()
            time.sleep(update_interval)


    @atexit.register
    def closing_app():
        db.close()

    ft.app(target=main, assets_dir="assets")
