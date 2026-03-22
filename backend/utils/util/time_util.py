# -*- coding: utf-8 -*-
import datetime
from datetime import date, timedelta
from app.tools.db_compatibility import DatabaseCompatibility


def get_week_start_and_end(n=0):
    """ 获取以当前日期所在周为坐标的 前/后n周开始时间和结束时间，参数n: 多少周，当前周以后的周数用负数 """
    now = datetime.datetime.now()
    n_week_start = now - datetime.timedelta(
        days=now.weekday() + 7 * n, hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond
    )
    n_week_end = n_week_start + datetime.timedelta(days=6, hours=23, minutes=59, seconds=59)
    return n_week_start, n_week_end


def get_now(str_format="%Y-%m-%d %H:%M:%S"):
    """ 获取当前时间 """
    if DatabaseCompatibility.is_postgresql():
        # PostgreSQL需要datetime对象
        return datetime.datetime.now()
    else:
        # MySQL可以使用字符串
        return datetime.datetime.now().strftime(str_format)


def time_calculate(days=0, str_format="%Y-%m-%d %H:%M:%S"):
    """ 以当前时间为坐标，获取指定天数之和的时间 """
    target_date = date.today() + timedelta(days=int(days))
    
    if DatabaseCompatibility.is_postgresql():
        # PostgreSQL需要datetime对象
        return datetime.datetime.combine(target_date, datetime.time.min)
    else:
        # MySQL可以使用字符串
        return target_date.strftime(str_format)


if __name__ == "__main__":
    start_time, end_time = get_week_start_and_end(1)
    print(f"start_time = {start_time}; end_time = {end_time}")
    print(time_calculate(1))
    print(get_now())
