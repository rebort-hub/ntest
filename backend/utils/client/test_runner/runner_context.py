# -*- coding: utf-8 -*-
import json
import re

from . import exceptions, parser, utils, validate_func


class SessionContext(object):
    """ TestRunner session

    Examples:
        >>> functions={...}
        >>> variables = {"SECRET_KEY": "DebugTalk"}
        >>> context = SessionContext(functions, variables)

        Equivalent to:
        >>> context = SessionContext(functions)
        >>> context.update_session_variables(variables)

    """
    def __init__(self, functions, variables=None):
        # 初始化时把当前测试用例运行结果标识为成功，后续步骤可根据此状态判断是否继续执行
        self.session_variables_mapping = utils.list_to_dict(variables or {"case_run_result": "success"})
        self.FUNCTIONS_MAPPING = functions
        # await self.init_test_variables()
        self.validation_results = []
        self.update_to_header = {}

    async def init_test_variables(self, variables_mapping=None):
        """ 初始化测试变量，在每个测试（api）开始时调用。变量映射将首先进行评估。

        Args:
            variables_mapping (dict)
                {
                    "random": "${gen_random_string(5)}",
                    "authorization": "${gen_md5($TOKEN, $data, $random)}",
                    "data": '{"name": "user", "password": "123456"}',
                    "TOKEN": "debugtalk",
                }

        """
        variables_mapping = variables_mapping or {}
        variables_mapping = utils.list_to_dict(variables_mapping)

        self.test_variables_mapping = {}
        # 提取的变量将覆盖预先定义好的变量
        self.test_variables_mapping.update(variables_mapping)
        self.test_variables_mapping.update(self.session_variables_mapping)

        for variable_name, variable_value in variables_mapping.items():
            variable_value = await self.eval_content(variable_value)
            self.update_test_variables(variable_name, variable_value)

    def update_test_variables(self, variable_name, variable_value):
        """ 更新变量，这些变量仅在当前测试中有效 """
        self.test_variables_mapping.setdefault(variable_name, variable_value)

    def update_session_variables(self, variables_mapping):
        """ 使用提取的变量映射更新会话。这些变量在整个运行会话中有效。"""
        variables_mapping = utils.list_to_dict(variables_mapping)
        self.session_variables_mapping.update(variables_mapping)
        self.test_variables_mapping.update(self.session_variables_mapping)

    def save_update_to_header_filed(self, filed_list: list, extracted_variables_mapping: dict):
        """ 把提取后需要更新到头部信息的数据保存下来
        filed_list: ['data']
        extracted_variables_mapping: {'data': 123, 'data2': 456}
        """
        for filed in filed_list:
            self.update_to_header[filed] = extracted_variables_mapping[filed]

    def update_filed_to_header(self, headers: dict):
        """ 把保存下来的需要更新到头部信息的字段更新到头部信息 """
        headers.update(self.update_to_header)
        return headers

    async def eval_content(self, content):
        """ 递归解析内容中的每个变量和函数。内容可以是任何数据结构，包括字典、列表、元组、数字、字符串等。"""
        return await parser.parse_data(
            content,
            self.test_variables_mapping,
            self.FUNCTIONS_MAPPING
        )

    async def __eval_check_item(self, validator, resp_obj):
        """ evaluate check item in validator.

        Args:
            validator (dict): validator
                {"check": "status_code", "comparator": "eq", "expect": 201}
                {"check": "$resp_body_success", "comparator": "eq", "expect": True}
            resp_obj (object): requests.Response() object

        Returns:
            dict: validator info
                {
                    "check": "status_code",
                    "check_value": 200,
                    "expect": 201,
                    "comparator": "eq"
                }

        """
        check_item = validator["check"]
        # check_item should only be the following 5 formats:
        # 1, variable reference, e.g. $token
        # 2, function reference, e.g. ${is_status_code_200($status_code)}
        # 3, dict or list, maybe containing variable/function reference, e.g. {"var": "$abc"}
        # 4, string joined by delimiter. e.g. "status_code", "headers.content-type"
        # 5, regex string, e.g. "LB[\d]*(.*)RB[\d]*"

        if isinstance(check_item, (dict, list)) \
            or parser.extract_variables(check_item) \
            or parser.extract_functions(check_item):
            # format 1/2/3
            check_value = await self.eval_content(check_item)
        elif re.compile(r".*\(.*\).*").match(check_item) or check_item.startswith(("content", "headers", "cookies")):  # 正则表达式或提取表达式
            check_value = resp_obj.extract_field(check_item)
        else:
            check_value = check_item

        validator["check_value"] = check_value

        # expect_value should only be in 2 types:
        # 1, variable reference, e.g. $expect_status_code
        # 2, actual value, e.g. 200
        expect_value = await self.eval_content(validator["expect"])
        validator["expect"] = expect_value
        validator["check_result"] = "unchecked"
        return validator

    def do_api_validation(self, validator_dict):
        """ 根据断言数据执行断言方法
        Args:
            validator_dict (dict): validator dict
                {
                    "check": "status_code",
                    "check_value": 200,
                    "expect": 201,
                    "comparator": "eq"
                }
        """
        comparator = validator_dict["comparator"]
        validate_func = parser.get_mapping_function(comparator, self.FUNCTIONS_MAPPING)
        check_item = validator_dict.get("check")
        check_value = validator_dict["check_value"]
        expect_value = validator_dict["expect"]
        check_value_type, expect_value_type = type(check_value).__name__, type(expect_value).__name__

        try:
            validator_dict["check_result"] = "pass"
            validate_func(check_value, expect_value)
            # logger.log_debug(f"断言: "
            #                  f"{check_item} "
            #                  f"{getattr(validate_func, comparator).__doc__} "
            #                  f"{expect_value}({type(expect_value).__name__}) "
            #                  f"==> pass")
        except (AssertionError, TypeError) as error:
            # 方便在页面上对比，转为dict
            try:
                if isinstance(expect_value, str):
                    expect_value = json.loads(expect_value)
            except Exception as json_loads_error:
                pass
            # 断言方式: {getattr(validate_func, comparator).__doc__}\n
            error_msg = f"""
            断言不通过\n
            断言方式: {validate_func.__doc__}\n
            预期结果: {expect_value}({expect_value_type})\n
            实际结果: {check_value}({check_value_type})\n
            描述：{error}
            """
            # 断言结果: {error}  # 断言未通过，断言方式为相等
            validator_dict["check_result"] = "fail"
            raise exceptions.ValidationFailure(error_msg)

    def do_ui_validation(self, driver, validator_dict):
        """ 根据断言数据执行断言方法
        Args:
            validator_dict (dict): validator dict
            {
                'comparator': 'assert_50is_exists',
                'check': ('xpath', '//*[@id="app"]/div/form/button/span'),
                'expect': '123123'
            }
        """
        check, expect, comparator = validator_dict["check"], validator_dict["expect"], validator_dict["comparator"]
        validate_func = getattr(driver, comparator)
        try:
            validator_dict["check_result"] = "pass"
            validate_func(check, expect)
            # logger.log_debug(f"断言: "
            #                  f"预期结果：{expect} "
            #                  f"断言方式：{validate_func.__doc__} "
            #                  f"断言元素：{check}"
            #                  f"==> 通过")
        except (AssertionError, TypeError) as error:
            error_msg = f"""
            断言不通过\n
            断言方式: {validate_func.__doc__}\n
            预期结果: {expect}\n
            断言元素: {check}\n
            描述：{error}
            """
            # 断言结果: {error}  # 断言未通过，断言方式为相等
            validator_dict["check_result"] = "fail"
            raise exceptions.ValidationFailure(error_msg)

    async def validate(self, validators, test_type, resp_obj=None, driver=None):
        """ 执行断言
        [{'_01equals': ['content', 'True']}]
        """
        self.validation_results = []
        if not validators:
            return

        validate_pass = True
        failures = []

        for validator in validators:
            # evaluate validators with context variable mapping.
            if validator.get("check") is None:  # 数据校验，已经解析过了
                evaluated_validator = await self.__eval_check_item(parser.parse_validator(validator), resp_obj)
            else:
                evaluated_validator = validator
            try:
                if validator.get("check") is None:  # 数据校验，已经解析过了
                    self.do_api_validation(evaluated_validator)
                else:
                    self.do_ui_validation(driver, evaluated_validator)
            except exceptions.ValidationFailure as ex:
                validate_pass = False
                failures.append(str(ex))

            self.validation_results.append(evaluated_validator)

        if not validate_pass:  # 断言未通过
            failures_string = "\n".join([failure for failure in failures])
            raise exceptions.ValidationFailure(failures_string)
