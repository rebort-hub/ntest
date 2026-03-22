# -*- coding: utf-8 -*-
def parse_cron(expression):
    """ 解析定时任务的时间
     入参 "0,30 1-55 * * * * "
     返回 {"second": "0,30", "minute": "1-55", "hour": "*", "day": "*", "month": "*", "day_of_week": "*"}
     """
    args = {}
    expression = expression.split(" ")
    if expression[0] != "?":
        args["second"] = expression[0]
    if expression[1] != "?":
        args["minute"] = expression[1]
    if expression[2] != "?":
        args["hour"] = expression[2]
    if expression[3] != "?":
        args["day"] = expression[3]
    if expression[4] != "?":
        args["month"] = expression[4]
    if expression[5] != "?":
        args["day_of_week"] = expression[5]
    return args
