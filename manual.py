''' 新股开板提醒 '''
import json
import signal
import sys
from threading import Thread
from time import sleep

from win32con import (HWND_TOPMOST, SWP_NOACTIVATE, SWP_NOMOVE,
                      SWP_NOOWNERZORDER, SWP_SHOWWINDOW)

from global_obj import Global
from strategy import *
from win32api import GetConsoleTitle, SetConsoleTitle
from win32gui import FindWindow, SetForegroundWindow, SetWindowPos

ths = []


def sigint_handler(signum, frame):
    Global.exited_flag = True
    print("Exit...")
    sys.exit()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)

    SetConsoleTitle("Monitor")
    sleep(1)
    hwnd = FindWindow(None, "Monitor")
    SetForegroundWindow(hwnd)
    SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 500, 450, SWP_NOMOVE |
                 SWP_NOACTIVATE | SWP_NOOWNERZORDER | SWP_SHOWWINDOW)

    try:
        file_object = open(Global._dir + '\strategy.json', mode='r', encoding='UTF-8')
        strategies = json.load(file_object)
        file_object.close()
    except:
        print("无法读取配置文件")

    for s in strategies:
        th = Thread(target=eval(s['strategy']), args=(s,))
        th.setDaemon(True)
        th.start()
        ths.append(th)

    while True:
        alive = False
        for th in ths:
            alive = alive or th.is_alive()
            if alive:
                break
        if not alive:
            break
        sleep(1)
