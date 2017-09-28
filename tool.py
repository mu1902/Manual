import urllib
import smtplib
import time
from email.mime.text import MIMEText


def get_html(url, request_data=None, method='post', header=None):
    ''' 获取页面 '''
    try:
        if request_data:
            if method == 'post':
                data = urllib.parse.urlencode(request_data).encode('utf_8')
                req = urllib.request.Request(url, data)
            else:
                data = urllib.parse.urlencode(request_data)
                req = urllib.request.Request(url + data)
        else:
            req = urllib.request.Request(url)

        if header:
            for key in header:
                req.add_header(key, header[key])
        con = urllib.request.urlopen(req).read()
        return con
    except urllib.error.HTTPError as e:
        # print(e)
        return ''
    except urllib.error.URLError as e:
        # print(e)
        return ''


def send_email(to_list, subject, massage):
    mail_host = "smtp.exmail.qq.com"
    mail_user = "fund@fundbj.com"
    mail_pwd = "fed68390036"
    msg = MIMEText(massage, _subtype='plain', _charset='gb2312')
    msg['Subject'] = subject
    msg['From'] = mail_user
    msg['To'] = ";".join(to_list)
    server = smtplib.SMTP()
    server.connect(mail_host)
    server.login(mail_user, mail_pwd)
    server.sendmail(mail_user, to_list, msg.as_string())
    server.close()


def wait(t):
    n = int(t[:-1])
    if t[-1] == 's':
        time.sleep(n)
    elif t[-1] == 'm':
        time.sleep(n * 60)
    elif t[-1] == 'h':
        time.sleep(n * 60 * 60)
    else:
        time.sleep(0)


def output(title, message):
    print("-----" + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "-----")
    print(">>>>>" + title + "<<<<<")
    print(message)
    print("-----------------------------\n")


def read_log(path):
    try:
        file = open(path, 'r')
        content = file.readlines()
    finally:
        file.close()
    return content


def write_log(path, list):
    try:
        file = open(path, 'a')
        for i in list:
            file.write(i)
    finally:
        file.close()
