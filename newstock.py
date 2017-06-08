''' 新股开板提醒 '''
import signal
import sys
import json
import urllib.request
from time import sleep
from threading import Thread

import toast

DUR = 5
tn = toast.ToastNotification()


def sigint_handler(signum, frame):
    print("退出")
    tn.unregister()
    sys.exit()


def newstock(strategy):
    for s in strategy.para:
        if s[0] == '0' or s[0] == '3':
            url = strategy.url + 'sz' + s
        elif s[0] == '6':
            url = strategy.url + 'sh' + s
        else:
            continue
        req = urllib.request.Request(url)
        res = urllib.request.urlopen(
            req).read().decode('gb2312').split(',')

        end_y = float(res[2])
        current = float(res[3])
        turnover = float(res[9])
        buy1_v = float(res[10])
        buy1_p = float(res[11])

        ratio = buy1_v * buy1_p / turnover if turnover != 0 else 9999

        # th = Thread(target=tn.show, args=(s[:6], str(current), 2))
        # th.setDaemon(True)
        # th.start()
        print(s[:6] + str(current))
        # tn.show(s[:6], str(current), 2)
        # if current == 0:
        #     continue
        # if ratio < 3 or current < round(end_y * 1.1, 2):
        #     n = n + 1
        #     tn = toast.ToastNotification()
        #     tn.show("可能开板", s[:6] + '-' + res[0].split('"')[1] + "\n买一/成交额倍数：" + str(
        # round(ratio, 2)) + "\n现价：" + str(round(current, 2)) + "-涨停价：" +
        # str(round(end_y * 1.1, 2)), DUR)
    # w = 30 - n * DUR if n * DUR < 30 else 0
    sleep(30)
    n = 0


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)

    strategies = json.load('strategy.json')

    n = 0
    while True:
        # for s in strategies:
        eval(strategies[0].strategy)(strategies[0])
