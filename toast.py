from os import path
from time import sleep
import threading

from win32api import GetModuleHandle, PostQuitMessage
from win32con import (CW_USEDEFAULT, IDI_APPLICATION, IMAGE_ICON,
                      LR_DEFAULTSIZE, LR_LOADFROMFILE, WM_DESTROY, WM_USER,
                      WS_OVERLAPPED, WS_SYSMENU)
from win32gui import (NIF_ICON, NIF_INFO, NIF_MESSAGE, NIF_TIP, NIM_ADD,
                      NIM_DELETE, NIM_MODIFY, WNDCLASS, CreateWindow,
                      DestroyWindow, LoadIcon, LoadImage, RegisterClass,
                      Shell_NotifyIcon, UnregisterClass, UpdateWindow)


class ToastNotification(object):
    def __init__(self):
        self.wc = WNDCLASS()
        self.hinst = self.wc.hInstance = GetModuleHandle(None)
        self.wc.lpszClassName = str("Manual")
        self.wc.lpfnWndProc = {WM_DESTROY: self.destory}
        self.classAtom = RegisterClass(self.wc)
        self.wins = []

    def show(self, title="Notification", msg="Some Message", duration=10, icon_path=None):
        self.hwnd = CreateWindow(self.classAtom, "Notification", WS_OVERLAPPED | WS_SYSMENU,
                                 0, 0, CW_USEDEFAULT, CW_USEDEFAULT, 0, 0, self.hinst, None)
        UpdateWindow(self.hwnd)
        # self.wins.append(self.hwnd)

        if icon_path is not None:
            icon_path = path.realpath(icon_path)
        else:
            icon_path = "ICO/stock.ico"
        hicon = LoadImage(self.hinst, icon_path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE)

        nid = (self.hwnd, 0, NIF_ICON | NIF_MESSAGE | NIF_TIP, WM_USER + 20, hicon, "Tooltip")
        nid2 = (self.hwnd, 0, NIF_INFO, WM_USER + 20,
                hicon, "Balloon Tooltip", msg, 200, title)
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(NIM_MODIFY, nid2)

        sleep(duration)
        DestroyWindow(self.hwnd)
        # self.wins.remove(self.hwnd)
        return None

    def destory(self, hwnd, msg, wparam, lparam):
        nid = (hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0)
        return None

    def unregister(self):
        for hwnd in self.wins:
            DestroyWindow(hwnd)
        UnregisterClass(self.wc.lpszClassName, None)
        return None