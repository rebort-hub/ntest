# -*- coding: utf-8 -*-
import ast
import json
import re
import traceback

from app.models.assist.model_factory import Script
from . import exceptions, utils
from .compat import basestring, builtin_str, numeric_types
from .validate_func import load_builtin_functions
from utils.variables.regexp import variable_regexp, function_regexp, function_regexp_compile


def parse_string_value(str_value):
    """ 把能转成数字的字符串转成数字
    "123" => 123
    "12.2" => 12.3
    "abc" => "abc"
    "$var" => "$var"
    """
    try:
        return str_value if '-' in str_value else ast.literal_eval(str_value)
    except (ValueError, SyntaxError):
        return str_value


def extract_variables(content):
    """ 从content中提取所有变量名为$variable的变量
    Args:
        content (str): 字符串
    Returns:
        extract_variables("$variable") >> ["variable"]
        extract_variables("/blog/$postid") >> ["postid"]
        extract_variables("/$var1/$var2") >> ["var1", "var2"]
        extract_variables("abc") >> []
    """
    try:
        return re.findall(variable_regexp, content)
    except TypeError:
        return []


def extract_functions(content):
    """ 从content中提取所有变量名为${fun()}的函数
    Args:
        content (str): 字符串
    Returns:
        extract_functions("${func(5)}") >>> ["func(5)"]
        extract_functions("${func(a=1, b=2)}") >>> ["func(a=1, b=2)"]
        extract_functions("/api/1000?_t=${get_timestamp()}") >>> ["get_timestamp()"]
        extract_functions("/api/${add(1, 2)}") >>> ["add(1, 2)"]
        extract_functions("/api/${add(1, 2)}?_t=${get_timestamp()}") >>> ["add(1, 2)", "get_timestamp()"]
    """
    try:
        return re.findall(function_regexp, content)
    except TypeError:
        return []


def parse_function(content):
    """ 从字符串内容中解析函数名和参数。
    Args:
        content (str): 字符串
    Returns:
        parse_function("func()") >>> {'func_name': 'func', 'args': [], 'kwargs': {}}
        parse_function("func(5)") >>> {'func_name': 'func', 'args': [5], 'kwargs': {}}
        parse_function("func(1, 2)") >>> {'func_name': 'func', 'args': [1, 2], 'kwargs': {}}
        parse_function("func(a=1, b=2)") >>> {'func_name': 'func', 'args': [], 'kwargs': {'a': 1, 'b': 2}}
        parse_function("func(1, 2, a=3, b=4)") >>> {'func_name': 'func', 'args': [1, 2], 'kwargs': {'a':3, 'b':4}}
    """
    matched = function_regexp_compile.match(content)
    if not matched:
        raise exceptions.FunctionNotFound("{} not found!".format(content))
    function_meta = {"func_name": matched.group(1), "args": [], "kwargs": {}}
    args_str = matched.group(2).strip()
    if args_str == "":
        return function_meta
    args_list = args_str.split(',')
    for arg in args_list:
        arg = arg.strip()
        if '=' in arg:
            key, value = arg.split('=')
            function_meta["kwargs"][key.strip()] = parse_string_value(value.strip())
        else:
            function_meta["args"].append(parse_string_value(arg))

    return function_meta


def parse_validator(validator):
    """
    解析验证器
    Args:
        验证器可能有两种格式:
        格式1: 这是为了与以前的版本兼容而保留的
            {"check": "status_code", "comparator": "eq", "expect": 201}
            {"check": "$resp_body_success", "comparator": "eq", "expect": True}
        格式2: 推荐的新版本
            {'eq': ['status_code', 201]}
            {'eq': ['$resp_body_success', True]}
    Returns
            {
                "check": "status_code",
                "expect": 201,
                "comparator": "eq"
            }
    """
    validator_parse_error = exceptions.ParamsError(f"验证器错误: {validator}")
    if not isinstance(validator, dict):
        raise validator_parse_error

    if "check" in validator and len(validator) > 1:
        # 格式1
        check_item = validator.get("check")
        if "expect" in validator:
            expect_value = validator.get("expect")
        elif "expected" in validator:
            expect_value = validator.get("expected")
        else:
            raise validator_parse_error
        comparator = validator.get("comparator", "eq")
        comparator_str = validator.get("comparator_str")

    elif len(validator) == 1:
        # 格式2
        comparator = list(validator.keys())[0]
        compare_values = validator[comparator]
        # if not isinstance(compare_values, list) or len(compare_values) != 2:
        if not isinstance(compare_values, list):
            raise validator_parse_error
        check_item, expect_value, comparator_str = compare_values
    else:
        raise validator_parse_error

    return {"check": check_item, "expect": expect_value, "comparator": comparator, "comparator_str": comparator_str}


def substitute_variables(content, variables_mapping):
    """ substitute variables in content with variables_mapping

    Args:
        content (str/dict/list/numeric/bool/type): content to be substituted.
        variables_mapping (dict): variables mapping.

    Returns:
        substituted content.

    Examples:
        >>> content = {
                'request': {
                    'url': '/api/users/$uid',
                    'headers': {'token': '$token'}
                }
            }
        >>> variables_mapping = {"$uid": 1000}
        >>> substitute_variables(content, variables_mapping)
            {
                'request': {
                    'url': '/api/users/1000',
                    'headers': {'token': '$token'}
                }
            }

    """
    if isinstance(content, (list, set, tuple)):
        return [
            substitute_variables(item, variables_mapping)
            for item in content
        ]

    if isinstance(content, dict):
        substituted_data = {}
        for key, value in content.items():
            eval_key = substitute_variables(key, variables_mapping)
            eval_value = substitute_variables(value, variables_mapping)
            substituted_data[eval_key] = eval_value

        return substituted_data

    if isinstance(content, basestring):
        # content is in string format here
        for var, value in variables_mapping.items():
            if content == var:
                # content is a variable
                content = value
            else:
                if not isinstance(value, str):
                    value = builtin_str(value)
                content = content.replace(var, value)

    return content


async def parse_parameters(parameters, variables_mapping=None, functions_mapping=None):
    """ parse parameters and generate cartesian product.

    Args:
        parameters (list) parameters: parameter name and value in list
            parameter value may be in three types:
                (1) data list, e.g. ["iOS/10.1", "iOS/10.2", "iOS/10.3"]
                (2) call built-in parameterize function, "${parameterize(account.csv)}"
                (3) call custom function in debugtalk.py, "${gen_app_version()}"

        variables_mapping (dict): variables mapping loaded from testcase config
        functions_mapping (dict): functions mapping loaded from debugtalk.py

    Returns:
        list: cartesian product list

    Examples:
        >>> parameters = [
            {"user_agent": ["iOS/10.1", "iOS/10.2", "iOS/10.3"]},
            {"username-password": "${parameterize(account.csv)}"},
            {"app_version": "${gen_app_version()}"}
        ]
        >>> parse_parameters(parameters)

    """
    variables_mapping = variables_mapping or {}
    functions_mapping = functions_mapping or {}
    parsed_parameters_list = []

    parameters = utils.list_to_dict(parameters)
    for parameter_name, parameter_content in parameters.items():
        parameter_name_list = parameter_name.split("-")

        if isinstance(parameter_content, list):
            # (1) data list
            # e.g. {"app_version": ["2.8.5", "2.8.6"]}
            #       => [{"app_version": "2.8.5", "app_version": "2.8.6"}]
            # e.g. {"username-password": [["user1", "111111"], ["test2", "222222"]}
            #       => [{"username": "user1", "password": "111111"}, {"username": "user2", "password": "222222"}]
            parameter_content_list = []
            for parameter_item in parameter_content:
                if not isinstance(parameter_item, (list, tuple)):
                    # "2.8.5" => ["2.8.5"]
                    parameter_item = [parameter_item]

                # ["app_version"], ["2.8.5"] => {"app_version": "2.8.5"}
                # ["username", "password"], ["user1", "111111"] => {"username": "user1", "password": "111111"}
                parameter_content_dict = dict(zip(parameter_name_list, parameter_item))

                parameter_content_list.append(parameter_content_dict)
        else:
            # (2) & (3)
            parsed_parameter_content = await parse_data(parameter_content, variables_mapping, functions_mapping)
            if not isinstance(parsed_parameter_content, list):
                raise exceptions.ParamsError("parameters syntax error!")

            parameter_content_list = []
            for parameter_item in parsed_parameter_content:
                if isinstance(parameter_item, dict):
                    # get subset by parameter name
                    # {"app_version": "${gen_app_version()}"}
                    # gen_app_version() => [{'app_version': '2.8.5'}, {'app_version': '2.8.6'}]
                    # {"username-password": "${get_account()}"}
                    # get_account() => [
                    #       {"username": "user1", "password": "111111"},
                    #       {"username": "user2", "password": "222222"}
                    # ]
                    parameter_dict = {key: parameter_item[key] for key in parameter_name_list}
                elif isinstance(parameter_item, (list, tuple)):
                    # {"username-password": "${get_account()}"}
                    # get_account() => [("user1", "111111"), ("user2", "222222")]
                    parameter_dict = dict(zip(parameter_name_list, parameter_item))
                elif len(parameter_name_list) == 1:
                    # {"user_agent": "${get_user_agent()}"}
                    # get_user_agent() => ["iOS/10.1", "iOS/10.2"]
                    parameter_dict = {
                        parameter_name_list[0]: parameter_item
                    }

                parameter_content_list.append(parameter_dict)

        parsed_parameters_list.append(parameter_content_list)

    return utils.gen_cartesian_product(*parsed_parameters_list)


# ###############################################################################
# ##  parse content with variables and functions mapping
# ###############################################################################
#
def get_mapping_variable(variable_name, variables_mapping):
    """ 从变量映射中获取变量值

    Args:
        variable_name (str): variable name
        variables_mapping (dict): variables mapping
    Returns:
        映射变量的值
    Raises:
        exceptions.VariableNotFound: 找不到变量
    """
    try:
        return variables_mapping[variable_name]
    except KeyError:
        raise exceptions.VariableNotFound(f"引用的变量 【{variable_name}】 没有找到")


def get_mapping_function(function_name, functions_mapping):
    """ get function from functions_mapping,
        if not found, then try to check if builtin function.

    Args:
        variable_name (str): variable name
        variables_mapping (dict): variables mapping

    Returns:
        mapping function object.

    Raises:
        exceptions.FunctionNotFound: function is neither defined in debugtalk.py nor builtin.

    """
    if function_name in functions_mapping:
        return functions_mapping[function_name]

    try:
        # check if TestRunner builtin functions
        # from . import loader
        # built_in_functions = loader.load_builtin_functions()
        built_in_functions = load_builtin_functions()
        return built_in_functions[function_name]
    except KeyError:
        pass

    try:
        # check if Python builtin functions
        item_func = eval(function_name)
        if callable(item_func):
            # is builtin function
            return item_func
    except (NameError, TypeError):
        # is not builtin function
        raise exceptions.FunctionNotFound(f"自定义函数 【{function_name}】 没有找到")


async def parse_string_functions(content, variables_mapping, functions_mapping):
    """ 映射字符串中的函数
    Args:
        content (str): "abc${add_one(3)}def"
        variables_mapping (dict): 变量字典
        functions_mapping (dict): {"add_one": lambda x: x + 1}
    Returns:
        parse_string_functions(content, functions_mapping) >>> "abc4def"
    """
    functions_list = extract_functions(content)
    for func_content in functions_list:
        function_meta = parse_function(func_content)
        args = await parse_data(function_meta.get("args", []), variables_mapping, functions_mapping)
        kwargs = await parse_data(function_meta.get("kwargs", {}), variables_mapping, functions_mapping)
        func = get_mapping_function(function_meta["func_name"], functions_mapping)
        # 执行自定义函数，有可能会报错
        try:

            # eval_value = func(*args, **kwargs)
            eval_value = await Script.run_func(func, args, kwargs)
        except Exception as error:
            # 记录错误信息
            # FuncErrorRecord.create(
            #     name='执行自定义函数错误',
            #     detail=f'执行自定义函数【{func_name}】报错了 \n  args参数: {args} \n  kwargs参数: {kwargs} \n\n  '
            #            f'错误信息: \n{traceback.format_exc()}'
            # )
            #
            # # 发送自定义函数执行错误的信息
            # send_run_func_error_message(content={
            #     "title": "执行自定义函数错误",
            #     "detail": f'### {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} \n> '
            #               f'### 执行自定义函数【{func_name}】报错了 \n  args参数: {args} \n  kwargs参数: {kwargs} \n  '
            #               f'### 错误信息: {traceback.format_exc()} \n> '
            # })
            raise

        func_content = "${" + func_content + "}"
        if func_content == content:
            # content is a function, e.g. "${add_one(3)}"
            content = eval_value
        else:
            # content contains one or many functions, e.g. "abc${add_one(3)}def"
            content = content.replace(
                func_content,
                str(eval_value), 1
            )

    return content


async def parse_string_variables(content, variables_mapping, functions_mapping):
    """ 从字符串中，解析引用变量

    Args:
        content (str): string content to be parsed.
        variables_mapping (dict): variables mapping.

    Returns:
        str: parsed string content.

    Examples:
        >>> content = "/api/users/$uid"
        >>> variables_mapping = {"$uid": 1000}
        >>> parse_string_variables(content, variables_mapping, {})
            "/api/users/1000"

    """
    variables_list = extract_variables(content)
    for variable_name in variables_list:
        variable_value = get_mapping_variable(variable_name, variables_mapping)

        if variable_name == "request" and isinstance(variable_value, dict) \
                and "url" in variable_value and "method" in variable_value:
            # call setup_hooks action with $request
            for key, value in variable_value.items():
                variable_value[key] = await parse_data(
                    value,
                    variables_mapping,
                    functions_mapping
                )
            parsed_variable_value = variable_value
        elif "${}".format(variable_name) == variable_value:
            parsed_variable_value = variable_value
        else:
            parsed_variable_value = await parse_data(
                variable_value,
                variables_mapping,
                functions_mapping,
                raise_if_variable_not_found=False
            )
            variables_mapping[variable_name] = parsed_variable_value
        # TODO: replace variable label from $var to {{var}}
        if "${}".format(variable_name) == content:
            # content is a variable
            content = parsed_variable_value
        else:
            # content contains one or several variables
            if not isinstance(parsed_variable_value, str):
                parsed_variable_value = builtin_str(parsed_variable_value)

            content = content.replace(
                "${}".format(variable_name),
                parsed_variable_value, 1
            )

    return content


async def parse_data(content, variables_mapping=None, functions_mapping=None, raise_if_variable_not_found=True):
    """ 用变量映射解析内容
    Args:
        content (str/dict/list/numeric/bool/type): 要解析的内容
        variables_mapping (dict): 变量映射
        functions_mapping (dict): 方法映射
        raise_if_variable_not_found (bool): 如果设置为False，则在发生VariableNotFound异常时不会抛出。
    Returns:
        解析后的内容

    Examples:
        >>> content = {
                'request': {
                    'url': '/api/users/$uid',
                    'headers': {'token': '$token'}
                }
            }
        >>> variables_mapping = {"uid": 1000, "token": "abcdef"}
        >>> parse_data(content, variables_mapping)
            {
                'request': {
                    'url': '/api/users/1000',
                    'headers': {'token': 'abcdef'}
                }
            }

    """
    if content is None or isinstance(content, (numeric_types, bool, type)):
        return content

    if isinstance(content, (list, set, tuple)):
        return [
            await parse_data(
                item,
                variables_mapping,
                functions_mapping,
                raise_if_variable_not_found
            )
            for item in content
        ]

    if isinstance(content, dict):
        parsed_content = {}
        for key, value in content.items():
            parsed_key = await parse_data(
                key,
                variables_mapping,
                functions_mapping,
                raise_if_variable_not_found
            )
            parsed_value = await parse_data(
                value,
                variables_mapping,
                functions_mapping,
                raise_if_variable_not_found
            )
            parsed_content[parsed_key] = parsed_value

        return parsed_content

    if isinstance(content, basestring):
        # content is in string format here
        variables_mapping = utils.list_to_dict(variables_mapping or {})
        functions_mapping = functions_mapping or {}
        content = content.strip()

        try:
            # 提取并执行自定义函数
            content = await parse_string_functions(content, variables_mapping, functions_mapping)

            # 用公用变量替换字符串中的占位符
            content = await parse_string_variables(content, variables_mapping, functions_mapping)
        except exceptions.VariableNotFound:
            if raise_if_variable_not_found:
                raise

    return content


async def parse_test_config(config, project_mapping):
    """ 解析测试用例的配置, 包括变量和名称。"""
    variables_mapping = utils.list_to_dict(config.pop("variables", {}))
    override_variables = utils.deepcopy_dict(project_mapping.get("variables", {}))
    variables_mapping.update(override_variables)
    parsed_variables = {}
    functions = project_mapping.get("functions", {})

    for key in variables_mapping:
        parsed_value = await parse_data(variables_mapping[key], variables_mapping, functions, False)
        variables_mapping[key] = parsed_value
        parsed_variables[key] = parsed_value

    if parsed_variables:
        config["variables"] = parsed_variables

    config["name"] = await parse_data(config.get("name", ""), parsed_variables, functions)

    if "base_url" in config:
        config["base_url"] = await parse_data(config["base_url"], parsed_variables, functions)


async def parse_test_step(steps: list, case_config: dict, project_mapping: dict):
    """ 解析测试步骤

        变量解析优先级:
        testcase config > testcase test > testcase_def config > testcase_def test > api
        用例级别 > 步骤级别 > 步骤级别 >

        base_url解析优先级:
        testcase test > testcase config > testsuite test > testsuite config > api
        用例级别 > 步骤级别 > 步骤级别 >

        verify priority:
        testcase teststep (api) > testcase config > testsuite config

    UI自动化：
        [{
            "extract": [{"c": "content.c"}],
            "name": "post请求",
            "action": {
            "action": "click",
            "by_type": "by_type",
            "element": "element",
            "text": "text"
            },
            "times": 1,
            "validate": [{"equals": ["$c", 3]}]
        }]

    """
    if not case_config.get("browser_type", ''):  # 接口自动化
        config_variables = case_config.get("variables", {})
        config_base_url = case_config.pop("base_url", "")
        functions = project_mapping.get("functions", {})

        for step_dict in steps:

            # base_url 优先使用步骤指定的，如果没有，则使用用例配置指定的
            step_dict["base_url"] = step_dict.get("base_url") or config_base_url

            # 合并步骤和用例配置的变量，相同key的值以用例配置的为准
            step_dict["variables"] = utils.extend_variables(step_dict.pop("variables", {}), config_variables)

            for key in step_dict["variables"]:
                parsed_key = await parse_data(key, step_dict["variables"], functions, False)
                parsed_value = await parse_data(step_dict["variables"][key], step_dict["variables"], functions, False)
                if parsed_key in step_dict["variables"]:
                    step_dict["variables"][parsed_key] = parsed_value

            # 测试步骤名字
            step_dict["name"] = await parse_data(step_dict.pop("name", ""), step_dict["variables"], functions, False)

            if step_dict.get("base_url"):  # 解析 base_url
                base_url = await parse_data(step_dict.pop("base_url"), step_dict["variables"], functions)
                url = step_dict["request"]["url"]
                step_dict["request"]["url"] = base_url + url if not url.lower().startswith('http') else url

    else:  # UI 自动化
        # 用例中配置的浏览器信息
        browser_type, browser_path = case_config.get("browser_type", ''), case_config.get("browser_path", '')

        # 用例中配置变量、自定义函数
        config_variables, functions = case_config.get("variables", {}), project_mapping.get("functions", {})

        for step in steps:
            step["variables"] = utils.extend_variables(step.pop("variables", {}), config_variables)  # 合并自定义变量

            # 把浏览器相关信息加到步骤中
            step.setdefault("browser_type", browser_type)
            step.setdefault("browser_path", browser_path)

            # 处理变量本身，有变量本身就有引用变量的情况
            for key in step["variables"]:
                parsed_key = await parse_data(key, step["variables"], functions, False)
                parsed_value = await parse_data(step["variables"][key], step["variables"], functions, False)
                if parsed_key in step["variables"]:
                    step["variables"][parsed_key] = parsed_value

            # 测试步骤名字
            step["name"] = await parse_data(step.pop("name", ""), step["variables"], functions, False)


async def parse_test_case(testcase, project_mapping):
    """ 解析测试用例和测试步骤
    Args:
        testcase: {"config": {}, "teststeps": []}
    """
    testcase.setdefault("config", {})
    await parse_test_config(testcase["config"], project_mapping)
    await parse_test_step(testcase["step_list"], testcase["config"], project_mapping)


async def parse_test_data(tests_dict, report_case_id):
    """ 解析测试数据

    Args:
        tests_dict (dict): project info and testcases list.

            {
                "project_mapping": {"PWD": "XXXXX", "functions": {}, "variables": {}, "env": {}},
                "project": {},
                "case_list": [
                    {
                    "config": {"name": "desc1", "path": "testcase1_path", "variables": {}},
                    "step_list": [
                            {'name': 'test step desc1', 'variables': [], 'extract': [], 'validate': [], 'request': {}}
                        ]
                    }
                ]
            }

        report_case_id: 测试报告用例的id
    """
    parsed_tests_mapping = {
        "project": tests_dict.get("project", {}),
        "project_mapping": tests_dict.get("project_mapping", {}),
        "report_id": tests_dict["report_id"],
        "report_model": tests_dict["report_model"],
        "report_case_model": tests_dict["report_case_model"],
        "report_step_model": tests_dict["report_step_model"],
        "response_time_level": tests_dict["response_time_level"],
        "test_case": []
    }

    report_case = await tests_dict["report_case_model"].filter(id=report_case_id).first()
    report_case.case_data["report_case_id"] = report_case.id

    test_case_mapping = {
        "config": report_case.case_data,
        "step_list": await tests_dict["report_step_model"].get_test_step_by_report_case(report_case.id)
    }
    test_case_mapping["config"]["pause_step_time_out"] = tests_dict["pause_step_time_out"]
    try:
        await parse_test_case(test_case_mapping, tests_dict.get("project_mapping", {}))
    except Exception as error:
        # exceptions.FunctionNotFound
        summary = report_case.summary
        summary["result"] = 'error'
        await report_case.test_is_error(summary=summary, error_msg=traceback.format_exc())
        return summary
    parsed_tests_mapping["test_case_mapping"] = test_case_mapping
    return parsed_tests_mapping

    # for testcase in tests_dict["case_list"]:
    #     # 如果解析用例报错了，就记录并跳过这条用例
    #     try:
    #         await parse_test_case(testcase, project_mapping)
    #     except Exception as error:
    #         report_case_data = await report_case.filter(id=testcase["config"]["report_case_id"]).first()
    #         summary = json.loads(report_case_data.summary)
    #         summary["success"] = 'error'
    #         await report_case_data.test_is_error(summary=summary, error_msg=error)
    #         continue
    #     parsed_tests_mapping["case_list"].append(testcase)
    #
    # return parsed_tests_mapping
