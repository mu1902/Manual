import datetime
import json

from pyquery import PyQuery as pq

import toast
import tool
from globalval import exited

DUR = 5


def newstock(strategy, flag=0):
    global exited
    tn = toast.ToastNotification(strategy['strategy'])
    while not exited:
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
                tn.show(strategy['name'], s[:6] + '-' + res[0].split('"')[1] + "\n买一/成交额倍数：" + str(
                    round(ratio, 2)) + "\n现价：" + str(round(current, 2)) + "-涨停价：" +
                    str(round(end_y * 1.1, 2)), DUR)
        tool.wait(strategy['freq'])
    if exited:
        tn.unregister()
        print('Thread' + strategy['strategy'] + 'stoped')


def convertible(strategy, flag=0):
    global exited
    tn = toast.ToastNotification(strategy['strategy'])
    while not exited:
        res1 = tool.get_html(strategy['url'][0], {"keyWord": "可转债",
                                                  "beginDate": datetime.date.today().strftime('%Y-%m-%d'),
                                                  "endDate": datetime.date.today().strftime('%Y-%m-%d')}, 'get', {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063",
                                                                                                                  "Host": "query.sse.com.cn",
                                                                                                                  "Referer": "http://www.sse.com.cn/disclosure/listedinfo/announcement/"}).decode('UTF-8')
        items = json.loads(res1)["result"]
        # title,url,security_Code
        tn.show(strategy['name'], "上交所公告数：" + str(len(items)))

        res2 = tool.get_html(strategy['url'][1], {"noticeType": "0109",
                                                  "startTime": datetime.date.today().strftime('%Y-%m-%d'),
                                                  "endTime": datetime.date.today().strftime('%Y-%m-%d')}).decode('gb2312')
        items = pq(res2)('.td2 a').items()
        item_list = list(items)
        tn.show(strategy['name'], "深交所公告数：" + str(len(item_list)))
        tool.wait(strategy['freq'])
    if exited:
        tn.unregister()
        print('Thread' + strategy['strategy'] + 'stoped')
