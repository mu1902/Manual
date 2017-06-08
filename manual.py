''' 新股开板提醒 '''
import json
import datetime
import signal
import sys
import urllib.request
from threading import Thread
from time import sleep

from pyquery import PyQuery as pq
import toast

DUR = 5


def sigint_handler(signum, frame):
    print("Exit...")
    sys.exit()


def get_html(url, request_data=None, method='post', header=None):
    ''' 获取页面 '''
    try:
        if request_data:
            data = urllib.parse.urlencode(request_data)
            if method == 'post':
                data.encode('utf-8')
                req = urllib.request.Request(url, data)
            else:
                req = urllib.request.Request(url + data)
        else:
            req = urllib.request.Request(url)

        if header:
            for key in header:
                req.add_header(key, header[key])
        con = urllib.request.urlopen(req).read()
        return con
    except urllib.error.HTTPError as e:
        print(e)
        return ''
    except urllib.error.URLError as e:
        print(e)
        return ''


def wait(t):
    n = int(t[:-1])
    if t[-1] == 's':
        sleep(n)
    elif t[-1] == 'm':
        sleep(n * 60)
    elif t[-1] == 'h':
        sleep(n * 60 * 60)
    else:
        sleep(0)


def newstock(strategy):
    tn = toast.ToastNotification(strategy['strategy'])
    for s in strategy['para']:
        if s[0] == '0' or s[0] == '3':
            url = strategy['url'][0] + 'sz' + s
        elif s[0] == '6':
            url = strategy['url'][0] + 'sh' + s
        else:
            continue
        res = get_html(url).decode('gb2312').split(',')

        end_y = float(res[2])
        current = float(res[3])
        turnover = float(res[9])
        buy1_v = float(res[10])
        buy1_p = float(res[11])

        ratio = buy1_v * buy1_p / turnover if turnover != 0 else 9999

        tn.show(s[:6], str(current))

        # if current == 0:
        #     continue
        # if ratio < 3 or current < round(end_y * 1.1, 2):
        #     n = n + 1
        #     tn = toast.ToastNotification()
        #     tn.show(strategy['name'], s[:6] + '-' + res[0].split('"')[1] + "\n买一/成交额倍数：" + str(
        # round(ratio, 2)) + "\n现价：" + str(round(current, 2)) + "-涨停价：" +
        # str(round(end_y * 1.1, 2)), DUR)
    wait(strategy['freq'])


def convertible(strategy):
    # tn = toast.ToastNotification(strategy['strategy'])
    # res2 = get_html(strategy['url'][1], {"noticeType": "0109",
    #                                      "startTime": datetime.date.today().strftime('%Y-%m-%d'),
    #                                      "endTime": datetime.date.today().strftime('%Y-%m-%d')}).decode('gb2312')
    # items = pq(res2)('.td2 a').items()
    # item_list = list(items)
    # tn.show(strategy['name'], "公告数：" + str(len(item_list)))

    res1 = get_html(strategy['url'][0], {"keyWord": "可转债",
                                         "beginDate": "2017-05-11",
                                         "endDate": "2017-06-08"}, 'get', {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063",
                                                                           "Host": "query.sse.com.cn",
                                                                           "Referer": "http://www.sse.com.cn/disclosure/listedinfo/announcement/"})
    print(res1.decode('UTF-8'))


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)

    try:
        file_object = open('strategy.json', mode='r', encoding='UTF-8')
        strategies = json.load(file_object)
    finally:
        file_object.close()

    # while True:
        # for s in strategies:
        # eval(strategies[0]['strategy'])(strategies[0])
    eval(strategies[1]['strategy'])(strategies[1])
