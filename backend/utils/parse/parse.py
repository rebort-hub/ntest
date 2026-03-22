# -*- coding: utf-8 -*-
import ast
import json
import re
from utils.variables.regexp import variable_regexp, function_regexp, function_regexp_compile


def parse_list_to_dict(data_list: list):
    """ list转字典，如果列表中有多个相同的key，则以最后一个为准 """
    result = {}
    for data in data_list:
        if data["key"]:
            result[data["key"]] = {
                "key": data.get("key"),
                "value": data.get("value"),
                "data_type": data.get("data_type"),
                "remark": data.get("remark")
            }
    return result


def parse_dict_to_list(data_dict: dict, add_row=True):
    """
    {
        "a": {
            "key": "a",
            "value": 123,
            "data_type": "str",
            "remark": "测试"
        }
    }
    """
    result = []
    for key, value in data_dict.items():
        result.append({
            "key": value.get("key"),
            "value": value.get("value"),
            "data_type": value.get("data_type"),
            "remark": value.get("remark")
        })
    if add_row:
        result.append({
            "key": None,
            "value": None,
            "data_type": None,
            "remark": None,
        })
    return result


def update_dict_to_list(from_dict: dict, to_list: list):
    """ 更新列表中的字典，返回更新后的列表 """
    variables = parse_list_to_dict(to_list)
    for key, value in from_dict.items():
        variables.setdefault(key, value)
    return parse_dict_to_list(variables)


def extract_functions(content):
    """ 从字符串内容中提取所有自定义函数，格式为${fun()}
    @param (str) content
    @return (list) functions list

    e.g. ${func(5)} => ["func(5)"]
         ${func(a=1, b=2)} => ["func(a=1, b=2)"]
         /api_1_0/1000?_t=${get_timestamp()} => ["get_timestamp()"]
         /api_1_0/${add(1, 2)} => ["add(1, 2)"]
         "/api_1_0/${add(1, 2)}?_t=${get_timestamp()}" => ["add(1, 2)", "get_timestamp()"]
    """
    try:
        return re.findall(function_regexp, content)
    except TypeError:
        return []


def extract_variables(content):
    """ 从内容中提取所有变量名，格式为$variable
    @param (str) content
    @return (list) variable name list

    e.g. $variable => ["variable"]
         /blog/$postid => ["postid"]
         /$var1/$var2 => ["var1", "var2"]
         abc => []
    """
    try:
        return re.findall(variable_regexp, content)
    except TypeError:
        return []


def convert(variable):
    """ 同层次参数中，存在引用关系就先赋值
    eg:
        phone:123
        name:$phone
            ↓↓↓↓
        phone:123
        name:123
    """
    _temp = json.dumps(variable)
    content = {v["key"]: v["value"] for v in variable if v["key"] != ""}
    for variable_name in extract_variables(_temp):
        if content.get(variable_name):
            # content contains one or several variables
            _temp = _temp.replace("${}".format(variable_name), str(content.get(variable_name)), 1)
            content = {v["key"]: v["value"] for v in json.loads(_temp) if v["key"] != ""}

    return _temp


def parse_string_value(str_value):
    """ 字符串内容若能转为数字则转为数字
    e.g. "123" => 123
         "12.2" => 12.3
         "abc" => "abc"
         "$var" => "$var"
    """
    try:
        return ast.literal_eval(str_value)
    except ValueError:
        return str_value
    except SyntaxError:
        # e.g. $var, ${func}
        return str_value


def encode_object(obj):
    """ json.dumps转化时，先把属于bytes类型的解码，若解码失败返回str类型，和其他对象属性统一转化成str"""
    if isinstance(obj, bytes):
        try:
            return bytes.decode(obj)
        except Exception as e:
            return str(obj)
    else:
        return str(obj)

    # raise TypeError("{} is not JSON serializable".format(obj))


if __name__ == "__main__":
    # func_list = importlib.reload(importlib.import_module(r"func_list.abuild_in_fun.py"))
    # module_functions_dict = {name: item for name, item in vars(func_list).items() if
    #                          isinstance(item, types.FunctionType)}
    # print(module_functions_dict)
    a = '${func({"birthday": "199-02-02"; "expire_age": "65周岁"; "sex": "2"},123,3245)}'
    b = "${func([123],123)}"
    print(extract_functions(a))
    # matched = parse_function(extract_functions(b)[0])
    #
    # print(matched)
