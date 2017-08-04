import datetime
import json
import threading
import time
import numpy as np
import pandas as pd

import wrapt
from pyquery import PyQuery as pq

import tool
from global_obj import Global
from WindPy import w


# lock = threading.Lock()
mail_list = ["wujg@fundbj.com", "zhongc@fundbj.com",
             "xuex@fundbj.com", "zhengy@fundbj.com", "chuh@fundbj.com"]


@wrapt.decorator
def log(wrapped, instance, args, kwargs):
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) +
          ' Thread: ' + args[0]['strategy'] + ' started')
    wrapped(*args, **kwargs)
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) +
          ' Thread: ' + args[0]['strategy'] + ' stoped')


@log
def newstock(strategy):
    while not Global.exited_flag:
        d = datetime.datetime.now()
        d1 = datetime.datetime.now().replace(hour=9, minute=25, second=0, microsecond=0)
        d2 = datetime.datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)
        in_time = d > d1 and d < d2
        if not in_time:
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

            ratio = buy1_v * buy1_p / turnover if turnover != 0 else 99999
            buy1_e = buy1_v * buy1_p

            if current == 0 or buy1_v == 0:
                continue
            if ratio < 5 or (buy1_e < 5 * 10**7 and ratio < 10) or current < round(end_y * 1.1, 2):
                # lock.acquire()
                text1 = s[:6] + '-' + res[0].split('"')[1] + "\n"
                text2 = "买一总额倍数：" + str(round(ratio, 2)) + "\n"
                text3 = "买一额：" + str(round(buy1_e / 10000, 0)) + "万\n"
                text4 = "现价：" + str(round(current, 2)) + \
                    "-涨停价：" + str(round(end_y * 1.1, 2))
                tool.output(strategy['name'], text1 + text2 + text3 + text4)
                # lock.release()
        delta = (d - d1).seconds / 60
        if delta < 10:
            tool.wait(strategy['freq1'])
        else:
            tool.wait(strategy['freq'])


@log
def convertible(strategy):
    while not Global.exited_flag:
        # 上交所
        res1 = tool.get_html(strategy['url'][0], {"title": "发行公告", "beginDate": strategy['begin'], "endDate": datetime.date.today().strftime('%Y-%m-%d')}, 'get', {
                             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063", "Host": "query.sse.com.cn", "Referer": "http://www.sse.com.cn/disclosure/listedinfo/announcement/"}).decode('UTF-8')
        items1 = json.loads(res1)["result"]  # title,URL,security_Code
        h_out = '\n'
        for i in items1:
            h_out += i["title"] + '\nhttp://www.sse.com.cn' + i["URL"] + '\n'

        # 深交所
        res2 = tool.get_html(strategy['url'][1], {"noticeType": "0109",
                                                  "keyword": "发行公告".encode('GB2312'),
                                                  "startTime": strategy['begin'],
                                                  "endTime": datetime.date.today().strftime('%Y-%m-%d')}).decode('GB2312')
        items2 = pq(res2)('.td2 a').items()  # <a href="PDF相对地址">公告名称</a>
        s_out = '\n'
        for i in items2:
            s_out += i.text() + '\nhttp://disclosure.szse.cn/m/' + i.attr("href") + '\n'

        if len(items1) > 0 or len(list(items2)) > 0:
            tool.send_email(["zhongc@fundbj.com", "chuh@fundbj.com"],
                            strategy['name'], h_out + s_out)
            tool.output(strategy['name'], "上交所：" + h_out + "\n深交所：" + s_out)
        tool.wait(strategy['freq'])


@log
def windIndex(strategy):
    d = datetime.date.today()
    d_begin = datetime.date.today() - datetime.timedelta(days=500)
    if d.day in strategy['period']:
        w.start()
        for g in strategy['para']:
            index = w.edb(g['code'], d_begin.strftime('%Y-%m-%d'),
                          d.strftime('%Y-%m-%d'), "Fill=Previous")
            if index.ErrorCode == 0:
                # df = pd.DataFrame({'date':index.Times,'data':index.Data[0]})
                # df.set_index('date', inplace=True)
                df = pd.DataFrame({'data': index.Data[0]}, index=index.Times)
                dfp = df.to_period()
                com = ((dfp['data'][-1] / dfp['data'][-2] - 1) * 100).round(2)
                seq = ((dfp['data'][-1] / dfp['data'][-12] - 1) * 100).round(2)
                message = g['name'] + " " + str(dfp.index[-1]) + \
                    "\n同比：" + str(com) + "%\n环比：" + str(seq) + "%"
                tool.output(strategy['name'], message)
                tool.send_email(mail_list, strategy['name'], message)
        w.stop()
