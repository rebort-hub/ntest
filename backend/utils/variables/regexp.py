# -*- coding: utf-8 -*-
import re

# 提取数据表达式的开头
extract_exp_start = (
    "status_code", "encoding", "ok", "reason", "url", "headers", "elapsed", "cookies", "content", "text", "json"
)

variable_regexp = r"\$([\w_]+)"  # 变量

function_regexp = r"\$\{([\w_]+\([\$\w\.\-/_ =,]*\))\}"  # 自定义函数

function_regexp_compile = re.compile(r"^([\w_]+)\(([\$\w\.\-/_ =,]*)\)$")

absolute_http_url_regexp = re.compile(r"^https?://", re.I)  # http请求

text_extractor_regexp_compile = re.compile(r".*\(.*\).*")


def is_extract_expression(expression):
    """ 判断字符串是否为提取表达式 """
    return text_extractor_regexp_compile.match(expression) or expression.startswith(extract_exp_start)
