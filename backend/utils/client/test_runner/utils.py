# -*- coding: utf-8 -*-
import copy
import json

from . import exceptions
from .compat import basestring
from .exceptions import ParamsError
from utils.variables.regexp import absolute_http_url_regexp


def build_url(base_url, path):
    """ 在接口地址前面加上域名，若设置的接口地址已包含域名，则直接返回 """
    if absolute_http_url_regexp.match(path):
        return path
    elif base_url:
        return "{}/{}".format(base_url.rstrip("/"), path.lstrip("/"))
    else:
        raise ParamsError(f"域名 '{base_url}' 错误, 请检查服务信息")


def query_json(json_content, query, delimiter='.'):
    """ 像xpath一样从json里面获取值
    Args:
        json_content (dict/list/string): {
            "person": {
                "name": {"first_name": "Leo"},
                "cities": ["Guangzhou", "Shenzhen"]
            }
        }
        query (str): 路径表达式字符串
        delimiter (str): 分隔符符号，默认为 "."
    Returns:
        query_json(json_content, "person.name.first_name") >> Leo
        query_json(json_content, "person.name.first_name.0") >> L
        query_json(json_content, "person.cities.0") >> Guangzhou
    """
    raise_flag = False
    response_body = u"response body: {}\n".format(json_content)
    try:
        for key in query.split(delimiter):
            if isinstance(json_content, (list, basestring)):
                json_content = json_content[int(key)]
            elif isinstance(json_content, dict):
                json_content = json_content[key]
            else:
                raise_flag = True
    except (KeyError, ValueError, IndexError):
        raise_flag = True

    if raise_flag:
        err_msg = u"数据提取失败! => {}\n".format(query)
        err_msg += response_body
        raise exceptions.ExtractFailure(err_msg)

    return json_content


def lower_dict_keys(origin_dict):
    """ 把字典的key转为小写
    Args:
        origin_dict (dict): {"URL": "", "METHOD": "", "Headers": ""}
    Returns:
        dict: {"url": "", "method": "", "headers": ""}
    """
    if not origin_dict or not isinstance(origin_dict, dict):
        return origin_dict

    return {key.lower(): value for key, value in origin_dict.items()}


def deepcopy_dict(data):
    """ 深拷贝字典，其中，忽略io对象 (_io.BufferedReader) """
    try:
        return copy.deepcopy(data)
    except TypeError:
        copied_data = {}
        for key, value in data.items():
            if isinstance(value, dict):
                copied_data[key] = deepcopy_dict(value)
            else:
                try:
                    copied_data[key] = copy.deepcopy(value)
                except TypeError:
                    copied_data[key] = value

        return copied_data


def list_to_dict(variables):
    """ list转字典
    入参：[{"a": 1}, {"b": 2}]
    返回：{"a": 1, "b": 2}
    """
    if isinstance(variables, list):
        variables_dict = {}
        for map_dict in variables:
            variables_dict.update(map_dict)

        return variables_dict

    elif isinstance(variables, dict):
        return variables

    else:
        raise exceptions.ParamsError("variables参数格式错误")


def extend_variables(variables1, variables2):
    """ raw_variables转字典后 继承 override_variables转为的字典
    Args:
        variables1 (list): [{"var1": "val1"}, {"var2": "val2"}]
        variables2 (list): [{"var1": "val111"}, {"var3": "val3"}]
    Returns:
        dict: {'var1', 'val111', 'var2', 'val2', 'var3', 'val3'}
    """
    if not variables1:
        override_variables_mapping = list_to_dict(variables2)
        return override_variables_mapping

    elif not variables2:
        raw_variables_mapping = list_to_dict(variables1)
        return raw_variables_mapping

    else:
        raw_variables_mapping = list_to_dict(variables1)
        override_variables_mapping = list_to_dict(variables2)
        raw_variables_mapping.update(override_variables_mapping)
        return raw_variables_mapping


def omit_long_data(body, omit_len=512):
    """ 处理 str / bytes 的长数据 """
    if not isinstance(body, basestring):
        return body

    body_len = len(body)
    if body_len <= omit_len:
        return body

    omitted_body = body[0:omit_len]

    appendix_str = " ... OMITTED {} CHARACTORS ...".format(body_len - omit_len)
    if isinstance(body, bytes):
        appendix_str = appendix_str.encode("utf-8")

    return omitted_body + appendix_str


def get_dict_data(content):
    if isinstance(content, dict):
        return content
    try:
        return json.loads(content)
    except Exception as error:
        return content
