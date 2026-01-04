# -*- coding: utf-8 -*-

import json
import datetime


def utils_template_get_current_time():
    """ 获取当前时间 """
    return int(datetime.datetime.now().timestamp())


def utils_template_dict_to_json(data):
    """ 字典转json """
    return json.dumps(data)
