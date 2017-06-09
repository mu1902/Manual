''' 新股开板提醒 '''
import json
import signal
import sys
from threading import Thread

from strategy import newstock
from strategy import convertible
from globalval import exited

ths = []

def sigint_handler(signum, frame):
    exited.flag = True
    # print("Wait to Exit...")
    print("Exit...")
    sys.exit()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)

    try:
        file_object = open('strategy.json', mode='r', encoding='UTF-8')
        strategies = json.load(file_object)
    finally:
        file_object.close()

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

    print("Exit...")