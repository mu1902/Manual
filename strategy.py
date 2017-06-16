import datetime
import json
import threading
import time

import wrapt
from pyquery import PyQuery as pq

import toast
import tool
from globalval import exited

DUR = 5
lock = threading.Lock()


@wrapt.decorator
def log(wrapped, instance, args, kwargs):
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) +
          ' Thread: ' + args[0]['strategy'] + ' started')
    wrapped(*args, **kwargs)
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) +
          ' Thread: ' + args[0]['strategy'] + ' stoped')


@log
def newstock(strategy):
    tn = toast.ToastNotification(strategy['strategy'])
    while not exited.flag:
        d = datetime.datetime.now()
        d1 = datetime.datetime.now().replace(hour=9, minute=25, second=0, microsecond=0)
        d2 = datetime.datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)
        in_time = d > d1 and d < d2
        if not in_time:
            print("Now is not trading time")
            tool.wait(strategy['freq'])
            continue

        for s in strategy['para']:
            if s[0] == '0' or s[0] == '3':
                url = strategy['url'][0] + 'sz' + s
            elif s[0] == '6':
                url = strategy['url'][0] + 'sh' + s
            else:
                continue
            res = tool.get_html(url).decode('gb2312').split(',')

            end_y = float(res[2])
            current = float(res[3])
            turnover = float(res[9])
            buy1_v = float(res[10])
            buy1_p = float(res[11])

            ratio = buy1_v * buy1_p / turnover if turnover != 0 else 9999

            if current == 0:
                continue
            if ratio < 5 or current < round(end_y * 1.1, 2):
                lock.acquire()
                tn.show(strategy['name'], s[:6] + '-' + res[0].split('"')[1] + "\n买一总额倍数：" + str(
                    round(ratio, 2)) + "\n现价：" + str(round(current, 2)) + "-涨停价：" +
                    str(round(end_y * 1.1, 2)), DUR)
                lock.release()
        tool.wait(strategy['freq'])
    tn.unregister()


@log
def convertible(strategy):
    tn = toast.ToastNotification(strategy['strategy'])
    while not exited.flag:
        # 上交所
        res1 = tool.get_html(strategy['url'][0], {"beginDate": strategy['begin'], "endDate": datetime.date.today().strftime('%Y-%m-%d')}, 'get', {
                             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063", "Host": "query.sse.com.cn", "Referer": "http://www.sse.com.cn/disclosure/listedinfo/announcement/"}).decode('UTF-8')
        items1 = json.loads(res1)["result"]  # title,url,security_Code

        # 深交所
        res2 = tool.get_html(strategy['url'][1], {"noticeType": "0109",
                                                  "startTime": strategy['begin'],
                                                  "endTime": datetime.date.today().strftime('%Y-%m-%d')}).decode('gb2312')
        items2 = pq(res2)('.td2 a').items()
        item_list = list(items2)
        # <a href="PDF相对地址">公告名称</a>

        lock.acquire()
        tn.show(strategy['name'], "上交所：" + str(len(items1)) + "\n深交所：" + str(len(item_list)), DUR)
        lock.release()

        tool.wait(strategy['freq'])
    tn.unregister()
