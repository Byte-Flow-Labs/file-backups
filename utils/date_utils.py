import re
import time
from datetime import datetime


def get_timezone(longitude):
    """
    通过经度计算时区
    :param longitude:
    :return:
    """
    # print(round(n))
    return round(longitude/15)


def get_local_timezone():
    """
    获取当前时区
    :return:
    """
    return int((datetime.now() - datetime.utcnow()).seconds / 3600)


def parse_format_time(stime):
    """
    解析时间
    :param stime: yyyy-mm-dd hh:MM:ss
    :return:
    """
    timestamp = 0
    try:
        pattern = re.compile(r'\d+')
        match_result = pattern.findall(stime)
        if match_result and len(match_result) >= 6:
            new_stime = ''
            for i in range(6):
                new_stime += match_result[i] + '-'
            timestamp = time.mktime(time.strptime(new_stime.strip(), '%Y-%m-%d-%H-%M-%S-'))
    except Exception as e:
        print(e)
    return int(timestamp)

