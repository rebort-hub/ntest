# -*- coding: utf-8 -*-
import re

from app.models.assist.model_factory import Script
from . import utils
from .compat import OrderedDict
from .parser import extract_functions, parse_function, get_mapping_variable, extract_variables

text_extractor_regexp_compile = re.compile(r".*\(.*\).*")


async def extract_by_data(
        extract_type,
        session_context_variables_mapping: dict,
        session_context,
        value: str):
    """ 执行自定义函数提取数据 """
    functions = extract_functions(value)
    if functions:
        extract_function_data = parse_function(functions[0])
        extract_arg_data = []  # arg
        for arg in extract_function_data.get('args', []):
            # 判断是常量还是自定义变量，如果是自定义变量，则替换
            variable = extract_variables(arg)
            if variable:
                extract_arg_data.append(get_mapping_variable(variable[0], session_context_variables_mapping))
            else:
                extract_arg_data.append(arg)

        extract_kwarg_data = {}  # kwarg
        for key, value in extract_function_data.get('kwargs', {}).items():
            # 判断是常量还是自定义变量，如果是自定义变量，则替换
            variable = extract_variables(value)
            if variable:
                extract_kwarg_data[key] = get_mapping_variable(variable[0], session_context_variables_mapping)
            else:
                extract_kwarg_data[key] = value

        # 执行自定义函数
        extract_function_data['args'], extract_function_data['kwargs'] = extract_arg_data, extract_kwarg_data

        func = session_context.FUNCTIONS_MAPPING[extract_function_data['func_name']]
        return await Script.run_func(func, extract_function_data['args'], extract_function_data['kwargs'])
        # return session_context.FUNCTIONS_MAPPING[extract_function_data['func_name']](
        #     *extract_function_data['args'],
        #     **extract_function_data['kwargs']
        # )
    else:
        if extract_type == "const":  # 常量
            return value
        elif extract_type == "variable":  # 变量：variable.$data.data 或者 variable.$data
            variable_expression_split = value.split(".", 1)
            if len(variable_expression_split) > 1:  # $data.data
                variable, extract_expression = variable_expression_split
                variable_data = extract_variables(variable)[0]
                return utils.query_json(
                    get_mapping_variable(variable_data, session_context_variables_mapping),
                    extract_expression
                )
            else:  # $data
                variable_data = extract_variables(variable_expression_split[0])[0]
                return get_mapping_variable(variable_data, session_context_variables_mapping)


def extract_by_element(driver, value: dict):
    """ 从响应数据中提取数据 """
    action_name = value.get('action')
    action_func = getattr(driver, action_name)
    return action_func((value.get('by_type'), value.get('element')))


async def extract_data(session_context, driver, extractors):
    """ 执行数据提取，并储存到 OrderedDict对象
    Args:
        extractors (list):
            [
                {"resp_status_code": "status_code"},
                {"resp_headers_content_type": "headers.content-type"},
                {"resp_content": "content"},
                {"resp_content_person_first_name": "content.person.name.first_name"}
            ]
    Returns:
        OrderDict: variable binds ordered dict
    """
    if not extractors:
        return {}

    extracted_variables_mapping = OrderedDict()
    session_context_variables_mapping = session_context.test_variables_mapping
    for extractor in extractors:
        result = None
        if extractor['type'] in ('const', 'func', 'variable'):  # 自定义函数、变量
            result = await extract_by_data(
                extractor['type'],
                session_context_variables_mapping,
                session_context,
                extractor['value']
            )

        elif extractor['type'] == 'element':  # 执行页面获取
            result = extract_by_element(driver, extractor['value'])

        extracted_variables_mapping[extractor['key']] = result
        session_context_variables_mapping[extractor['key']] = result

    return extracted_variables_mapping
