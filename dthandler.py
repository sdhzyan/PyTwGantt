#-*- coding:utf-8 -*-

import time,pytz
from datetime import datetime

def dt_to_int(datestr):
    '''
    :param datestr: 格式yyyy-mm-dd hh:mm:ss
    :return: 返回对应时间戳毫秒值
    '''
    #res={}
    #start_timest = datestr+' 00:00:00'
    #end_timest = datestr+' 23:59:59'
    #res['int_start_timest'] = int(round(time.mktime(time.strptime(start_timest, "%Y-%m-%d %H:%M:%S"))*1000))
    #res['int_end_timest'] = int(round(time.mktime(time.strptime(end_timest, "%Y-%m-%d %H:%M:%S"))*1000))
    return int(round(time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S"))*1000))

def int_to_dt(timestamp):
    '''
    :param timestamp: 时间戳毫秒值
    :return: 返回对应时间戳,格式yyyy-mm-dd hh:mm:ss(带时区)
    '''
    timest = timestamp/1000.0
    timearr = time.localtime(timest)

    #print time.strftime("%Y-%m-%d %H:%M:%S", timearr)

    return pytz.utc.localize(datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S", timearr),"%Y-%m-%d %H:%M:%S"))

def utc_to_cn_str(utc_datetime):
    '''
    :param utc_datetime: 带UTC时区的datetime
    :return: 返回对应中国区datetime字符串,格式yyyy-mm-dd hh:mm:ss
    '''
    return utc_datetime.astimezone(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")

if __name__ == '__main__':
    print dt_to_int('2017-12-20 00:00:00')
    print int_to_dt(dt_to_int('2017-12-20 00:00:00'))