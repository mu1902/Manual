''' 新股开板提醒 '''
import json
import signal
import sys
from threading import Thread

from strategy import newstock
from strategy import convertible
from globalval import exited

def sigint_handler(signum, frame):
    global exited
    exited = True
    print("Exit...")
    sys.exit()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)

    try:
        file_object = open('strategy.json', mode='r', encoding='UTF-8')
        strategies = json.load(file_object)
    finally:
        file_object.close()

    ths = []
    for s in strategies:
        th = Thread(target=eval(s['strategy']), args=(s, 0))
        th.setDaemon(True)
        th.start()
        ths.append(th)

    # for th in ths:
    #     th.join()
    while True:
        alive = False
        for th in ths:
            alive = alive or th.is_alive()
            if alive:
                break
        if not alive:
            break
