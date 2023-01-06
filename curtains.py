import base64
import ctypes
import os.path
import sys
from ctypes import wintypes
from io import BytesIO

import psutil
import pyinjector
import win32.lib.win32con as win32con
import win32api  # pip package pypiwin32; library is named win32; has to be imported this way
import win32gui  # pip package pypiwin32; library is named win32; has to be imported this way
import win32ui  # pip package pypiwin32; library is named win32; has to be imported this way
from PIL import Image
from PIL import ImageGrab
from pyinjector import inject

# detect if frozen pyinstaller exe to
if getattr(sys, 'frozen', False):
    BASEDIR = sys._MEIPASS
else:
    BASEDIR = os.path.dirname(os.path.abspath(__file__))


enumWindows = ctypes.windll.user32.EnumWindows
enumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.POINTER(ctypes.c_int))
getWindowText = ctypes.windll.user32.GetWindowTextW
getWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
# isWindowVisible = ctypes.windll.user32.IsWindowVisible

def all_hwnds():
    """returns a list of window handles for all visible windows."""
    hwnd_list = []

    def foreach_window(hwnd, lParam):
        if ctypes.windll.user32.IsWindowVisible(hwnd) != 0:
            hwnd_list.append(hwnd)

        return True

    enumWindows(enumWindowsProc(foreach_window), 0)

    return hwnd_list


def pid_of_hwnd(hwnd):
    '''returns the name of the executable that belongs to the window'''
    lpdw_process_id = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(lpdw_process_id))
    process_id = lpdw_process_id.value

    return process_id


def process_name_of_pid(pid):
    '''arg: PID, return: name of executable'''
    procname = psutil.Process(pid).name()
    return procname


def executable_path(name, pid):
    '''returns the path of a process e.g.: explorer.exe, 1432'''
    try:
        if psutil.Process(pid).name() == name:
            return psutil.Process(pid).exe()
    except Exception as e:
        print(e)
        print(f'ERROR finding process path for PID {pid} \n')


def username_of_pid(pid):
    '''arg: PID, return: name of user which runs the process'''
    uname = psutil.Process(pid).username()

    return uname


def extract_icon(exefilename, hwnd):
    """Get the first resource icon from exefilename and returns it as bytes array"""
    # fixme: throws errors around the 5000th repetition; not cool but works for this usecase
    ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
    try:
        large, small = win32gui.ExtractIconEx(exefilename, 0)

    except:
        return None

    if not large:

        return None

    else:
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(hwnd))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_x)
        hdc = hdc.CreateCompatibleDC()
        hdc.SelectObject(hbmp)
        hdc.DrawIcon((0, 0), large[0])
        bmpstr = hbmp.GetBitmapBits(True)
        img = Image.frombuffer('RGBA', (32, 32), bmpstr, 'raw', 'BGRA', 0, 1)
        win32gui.DestroyIcon(small[0])
        win32gui.DestroyIcon(large[0])

        return img


def image2base64(img):
    '''arg: image, return: utf-8 decoded base64 string'''
    buffered = BytesIO()
    img = img.convert('RGBA')
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    buffered.truncate()
    return img_str.decode("utf-8")


def hide_windows(pid):
    '''arg: PID; inject dll into that process to hide it'''
    # inject into process
    # 1.Try 64-bit dll
    try:
        inject(pid, (BASEDIR + r"/assets/Hide.dll"))

    except Exception as e:
        # print(f'{e}\n{pid} 64\n')
        # print(e)
        pass

    # 2.Try 32-bit dll
    try:
        inject(pid, (BASEDIR + r"/assets/Hide_32bit.dll"))

    except Exception as e:
        # print(f'{e}\n{pid} 32\n already hidden\n')
        # print(e)
        pass


def unhide_windows(pid):
    '''arg: PID; inject dll into that process to unhide it'''
    # inject into process
    # 1.Try 64-bit dll
    try:
        inject(pid, (BASEDIR + r"\assets\Unhide.dll"))

    except Exception as e:
        # print(f'{e}\n{pid} 64\n already visible\n')
        # print(e)
        pass
    # 2.Try 32-bit dll
    try:
        inject(pid, (BASEDIR + r"\assets\Unhide_32bit.dll"))

    except Exception as e:
        # print(f'{e}\n{pid} 32\n')
        # print(e)
        pass


def minimize_window(hwnd):
    '''arg: hwnd; minimizes the window '''
    ctypes.windll.user32.CloseWindow(hwnd)


def window_position(hwnd):
    '''arg: window handle(hwnd); return: left, top, right, bottom pixel position of a window'''
    rect = wintypes.RECT()
    ff = ctypes.windll.user32.GetWindowRect(hwnd, ctypes.pointer(rect))
    # print(rect.left, rect.top, rect.right, rect.bottom)
    return rect.left, rect.top, rect.right, rect.bottom


def to_foreground(hwnd):
    '''arg: window handle(hwnd), bring window to front'''
    ctypes.windll.user32.ShowWindow(hwnd, 5)
    ctypes.windll.user32.SetForegroundWindow(hwnd)


def window_title(hwnd):
    """arg: window handle(hwnd), return: title of window"""
    text_len_in_characters = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    string_buffer = ctypes.create_unicode_buffer(
        text_len_in_characters + 1)  # +1 for the \0 at the end of the null-terminated string.
    ctypes.windll.user32.GetWindowTextW(hwnd, string_buffer, text_len_in_characters + 1)

    # fixme: ambiguous if an error or title is empty.
    result = string_buffer.value
    if result == "":
        result = '<NO TITLE>'
    return result


def rename_window_title(hwnd, title=""):
    '''arg: window handle(hwnd), new title for that window'''
    try:
        ctypes.windll.user32.SetWindowTextW(hwnd, title)

    except Exception as e:
        print(e)
        pass


def return_screensize():
    '''returns the screensize/resolution for all displays'''
    ctypes.windll.user32.SetProcessDPIAware()
    width = ctypes.windll.user32.GetSystemMetrics(0)
    height = ctypes.windll.user32.GetSystemMetrics(1)
    return width, height


def take_screenshot():
    '''returns a screenshot of the whole screen; resized to quarter original size'''
    try:
        img = ImageGrab.grab()
        width, height = img.size
        img.resize((width // 4, height // 4))
        return img

    except Exception as e:
        print(e)


def is_black(img):
    '''arg: image; return: True if all pixels are black, else False'''
    # take screenshot
    # img = ImageGrab.grab()
    return not img.getbbox()

# def isvisible(hwnd):
#     # this does not work. needs to be called via dll injection to make it work
#     # print(ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x00000011))
#     # return ctypes.windll.user32.IsWindowVisible(hWnd)
#     #     ### not working as supposed
#     return bool(ctypes.windll.user32.GetWindowDisplayAffinity(hwnd))


# def getlayered(hwnd): did not need to use it in any case
#
#     # see https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getlayeredwindowattributes
#     return ctypes.windll.user32.GetLayeredWindowAttributes(hwnd)
