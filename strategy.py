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
        sh_res1 = tool.get_html(strategy['url'][0],
                                {"beginDate": strategy['begin'],
                                 "endDate": datetime.date.today().strftime('%Y-%m-%d')},
                                'get',
                                {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063",
                                 "Host": "query.sse.com.cn",
                                 "Referer": "http://www.sse.com.cn/disclosure/bond/announcement/convertible/"}
                                ).decode('UTF-8')
        sh_items1 = json.loads(sh_res1)["result"]  # security_Code证券代码
        sh_items1 = list(
            filter(lambda x: ('发行公告' in x["title"])or('中签' in x["title"])or('上市' in x["title"]), sh_items1))
        sh_out = '\n'
        for i in sh_items1:
            sh_out += i["title"] + '\nhttp://www.sse.com.cn' + i["URL"] + '\n'

        sh_res2 = tool.get_html(strategy['url'][1],
                                {"channelId": "9868", "sqlId": "BS_GGLL", "siteId": "28", "extGGDL": "1101", "extGGLX": "11",
                                 "createTime": strategy['begin'] + " 00:00:00",
                                 "createTimeEnd": datetime.date.today().strftime('%Y-%m-%d') + " 23:59:59"},
                                'get',
                                {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063",
                                 "Host": "query.sse.com.cn",
                                 "Referer": "http://www.sse.com.cn/disclosure/bond/announcement/exchangeable/"}
                                ).decode('UTF-8')
        sh_items2 = json.loads(sh_res2)["result"]
        sh_items2 = list(filter(lambda x: ('发行公告' in x["docTitle"])or(
            '中签' in x["docTitle"])or('上市' in x["docTitle"]), sh_items2))
        for i in sh_items2:
            sh_out += i["docTitle"] + '\nhttp://' + i["docURL"] + '\n'

        # 深交所
        sz_res1 = tool.get_html(strategy['url'][2],
                                {"noticeType": "0109",
                                 #  "keyword": "发行公告".encode('GB2312'),
                                 "startTime": strategy['begin'],
                                 "endTime": datetime.date.today().strftime('%Y-%m-%d')}).decode('GB2312')
        sz_items1 = pq(sz_res1)('.td2 a').items()  # <a href="PDF相对地址">公告名称</a>
        sz_items1 = list(
            filter(lambda x: ('发行公告' in x.text())or('中签' in x.text())or('上市' in x.text()), sz_items1))
        sz_out = '\n'
        for i in sz_items1:
            sz_out += i.text() + '\nhttp://disclosure.szse.cn/m/' + i.attr("href") + '\n'

        if (len(sh_items1) + len(sh_items2) + len(list(sz_items1))) > 0:
            tool.send_email(strategy['receiver'],
                            strategy['name'], sh_out + sz_out)
            tool.output(strategy['name'], "上交所：" + sh_out + "\n深交所：" + sz_out)
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


@log
def HKEX(strategy):
    def parse(arr, dic):
        for row in dic['content'][1]['table']['tr']:
            r = row['td'][0]
            if r[1] != '-':
                arr.append({
                    "code": r[1],
                    "name": r[2].replace('\u3000', ''),
                    "net": int(r[3].replace(',', '')) -
                    int(r[4].replace(',', ''))
                })

    def sign(arr):
        _arr = [n for n in arr[1:] if int(n) > 0]
        if len(_arr) == len(arr) or len(_arr) == 0:
            return True
        else:
            return False

    def identify(rows, n):
        reverse = {}
        for row in rows:
            if row['code'] in reverse:
                reverse[row['code']].append(row['net'])
            else:
                reverse[row['code']] = [row['name'], row['net']]

        reverse = {k: v for k, v in reverse.items() if len(v) ==
                   n + 1 and sign(v)}
        return reverse

    def date_title(dates, n):
        res = " " * n
        res += "  ".join(dates)
        res += "\n"
        return res

    def formatter(category, dic):
        res = category + "\n"
        for (k, v) in dic.items():
            res += "%6s " % (k)
            for (i, x) in enumerate(v):
                if i == 0:
                    res += "%4.4s " % (x)
                else:
                    res += "%11s " % (x)
            res += "\n"
        res += "\n"
        return res

    d = datetime.date.today()
    sh, hksh, sz, hksz, dates1 = ([], [], [], [], [])
    ndate = strategy['nDate'][0]
    while ndate > 0:
        if d.weekday() != 5 or d.weekday() != 6:
            t = datetime.datetime.now().timestamp()
            t_str = str(t * 1000)[0:13]
            param = 'data_tab_daily_' + d.strftime('%Y%m%d') + 'c.js?' + t_str
            html = tool.get_html(
                strategy['url'][0] + param, method='get')
            if html != "":
                data = json.loads(html.decode('utf-8').split(' = ')[1])
                # 沪股通
                parse(sh, data[0])
                # 港股通（沪）
                parse(hksh, data[1])
                # 深股通
                parse(sz, data[2])
                # 港股通（深）
                parse(hksz, data[3])
                dates1.append(d.strftime('%Y-%m-%d'))
                ndate = ndate - 1
        d = d - datetime.timedelta(days=1)

    message = "" + date_title(dates1, 17) + formatter("沪股通", identify(sh, strategy['nDate'][0])) + formatter("港股通（沪）", identify(
        hksh, strategy['nDate'][0])) + formatter("深股通", identify(sz, strategy['nDate'][0])) + formatter("港股通（深）", identify(hksz, strategy['nDate'][0]))

    message += "-----------------------------\n"

    d = datetime.date.today()
    hold = {k: [] for k in strategy['stock']}
    dates2 = []
    ndate = strategy['nDate'][1]

    while ndate > 0:
        if d.weekday() != 5 or d.weekday() != 6:
            html = tool.get_html(strategy['url'][1], {
                "ddlShareholdingDay": str(d.day),
                "ddlShareholdingMonth":  "0" * (2 - len(str(d.month))) + str(d.month),
                "ddlShareholdingYear": str(d.year)}, method='post').decode('utf-8')

            data = pq(html)(".result-table tr")
            for tr in data:
                td_pq = pq(tr)("td")
                if td_pq.eq(1).text() in strategy['stock']:
                    hold[td_pq.eq(1).text()].append(td_pq.eq(3).text())
            dates2.append(d.strftime('%Y-%m-%d'))
            ndate = ndate - 1
        d = d - datetime.timedelta(days=1)

    message += date_title(dates2, 13)
    for (k, vs) in hold.items():
        message += "  " * (6-len(k[:6])) + k[:6] + " "
        for v in vs:
            message += "%10s  " % (v)
        message += "\n"

    tool.output(strategy['name'], message)
    tool.send_email(strategy['receiver'], strategy['name'], message)
