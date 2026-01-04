# -*- coding: utf-8 -*-
import types

from utils.variables.regexp import text_extractor_regexp_compile, extract_exp_start


def is_function(item):
    """ 判断传进来的 item对象 是否为函数 """
    return isinstance(item, types.FunctionType)


def is_const(variable):
    try:
        return eval(str(variable))
    except:
        return False


def is_extract_expression(expression):
    """ 判断字符串是否为提取表达式 """
    return text_extractor_regexp_compile.match(expression) or expression.startswith(extract_exp_start)
