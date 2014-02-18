# -*- coding: utf-8 -*-
from datetime import datetime

_MINUTE = 60 # 1分钟
_HOUR = 60 * _MINUTE # 1小时
_DAY = 24 * _HOUR # 1天
_MONTH = 31 * _DAY # 月
_YEAR = 12 * _MONTH # 年

def convert(time):
    # TODO check time

    seconds = int((datetime.now() - time).total_seconds())
    if seconds == 0:
        return "刚刚"
    if seconds < 60:
        return str(seconds) + '秒前'
    minutes = seconds / _MINUTE
    if minutes < 60:
        return str(minutes) + '分钟前'
    hours = seconds / _HOUR
    if hours < 24:
       return str(hours) + '小时前'
    days = seconds / _DAY
    if days < 31:
        return str(days) + '天前'
    months = seconds / _MONTH
    if months < 12:
        return  str(months) + '月前'
    years = seconds / _YEAR
    return str(years) + '年前'

