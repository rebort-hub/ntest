# -*- coding: utf-8 -*-
import re

from . import exceptions, utils
from .compat import OrderedDict, basestring
from .parser import extract_functions, parse_function, get_mapping_variable
from utils.client.test_runner.parser import extract_variables
from .validator import is_extract_expression, is_const
from ...variables.regexp import text_extractor_regexp_compile


class ResponseObject(object):

    def __init__(self, resp_obj):
        """ 用请求的响应对象初始化响应信息
        Args:
            resp_obj (instance): requests.Response instance
        """
        self.resp_obj = resp_obj

    def __getattr__(self, key):
        try:
            if key == "json":
                value = self.resp_obj.json()
            elif key == "cookies":
                value = dict(self.resp_obj.cookies.items())
            elif key == "headers":
                value = dict(self.resp_obj.headers)
            else:
                value = getattr(self.resp_obj, key)

            self.__dict__[key] = value
            return value
        except AttributeError:
            err_msg = "响应对象中没有属性: {}".format(key)
            raise exceptions.ParamsError(err_msg)

    def _extract_field_with_regex(self, field):
        """ 从响应对象中提取数据，支持json和字符串
        Args:
            field (str): 正则字符串 r".*\(.*\).*"
        Returns:
            str: 匹配的内容
        Raises:
            如果没有与正则表达式匹配的内容则抛出异常 exceptions.ExtractFailure
        Examples:
            >>> # self.text: "LB123abcRB789"
            >>> filed = "LB[\d]*(.*)RB[\d]*"
            >>> _extract_field_with_regex(field)
            abc
        """
        matched = re.search(field, self.resp_obj.text)
        if not matched:
            err_msg = u"正则表达式提取数据失败! => {}\n".format(field)
            err_msg += u"response body: {}\n".format(self.resp_obj.text)
            raise exceptions.ExtractFailure(err_msg)

        return matched.group(1)

    def _extract_field_with_delimiter(self, field, variable_data=None):
        """ 响应内容可以是json或html文本
        Args:
            field (str): 由分隔符连接的字符串。
            e.g.
                "status_code"
                "headers"
                "cookies"
                "content"
                "headers.content-type"
                "content.person.name.first_name"
        """
        # string.split(sep=None, maxsplit=-1) -> list of strings
        # e.g. "content.person.name" => ["content", "person.name"]
        try:
            top_query, sub_query = field.split('.', 1)
        except ValueError:
            top_query = field
            sub_query = None

        # status_code
        if top_query in ["status_code", "encoding", "ok", "reason", "url"]:
            if sub_query:
                # status_code.XX
                err_msg = u"提取失败: {}\n".format(field)
                raise exceptions.ParamsError(err_msg)

            return getattr(self, top_query)

        # cookies
        elif top_query == "cookies":
            cookies = self.cookies
            if not sub_query:
                # extract cookies
                return cookies

            try:
                return cookies[sub_query]
            except KeyError:
                err_msg = u"cookie提取失败! => {}\n".format(field)
                err_msg += u"response cookies: {}\n".format(cookies)
                raise exceptions.ExtractFailure(err_msg)

        # elapsed
        elif top_query == "elapsed":
            available_attributes = u"可用属性: days, seconds, microseconds, total_seconds"
            if not sub_query:
                err_msg = u"elapsed is datetime.timedelta instance, attribute should also be specified!\n"
                err_msg += available_attributes
                raise exceptions.ParamsError(err_msg)
            elif sub_query in ["days", "seconds", "microseconds"]:
                return getattr(self.elapsed, sub_query)
            elif sub_query == "total_seconds":
                return self.elapsed.total_seconds()
            else:
                err_msg = "{} is not valid datetime.timedelta attribute.\n".format(sub_query)
                err_msg += available_attributes
                raise exceptions.ParamsError(err_msg)

        # headers
        elif top_query == "headers":
            headers = self.headers
            if not sub_query:
                # extract headers
                return headers

            try:
                return headers[sub_query]
            except KeyError:
                err_msg = u"提取头部信息失败 => {}\n".format(field)
                err_msg += u"头部信息: {}\n".format(headers)
                raise exceptions.ExtractFailure(err_msg)

        # 响应体
        elif top_query in ["content", "text", "json"]:
            try:
                body = self.json
            except exceptions.JSONDecodeError:
                body = self.text

            if not sub_query:
                # extract response body
                return body

            if isinstance(body, (dict, list)):
                # content = {"xxx": 123}, content.xxx
                return utils.query_json(body, sub_query)
            elif sub_query.isdigit():
                # content = "abcdefg", content.3 => d
                return utils.query_json(body, sub_query)
            else:
                # content = "<html>abcdefg</html>", content.xxx
                err_msg = f"从响应体提取数据失败 => {field}\n响应体: {body}\n"
                raise exceptions.ExtractFailure(err_msg)

        # 自定义变量
        elif top_query == "variable":
            return utils.query_json(variable_data, sub_query)

        # new set response attributes in teardown_hooks
        elif top_query in self.__dict__:
            attributes = self.__dict__[top_query]

            if not sub_query:
                # extract response attributes
                return attributes

            if isinstance(attributes, (dict, list)):
                # attributes = {"xxx": 123}, content.xxx
                return utils.query_json(attributes, sub_query)
            elif sub_query.isdigit():
                # attributes = "abcdefg", attributes.3 => d
                return utils.query_json(attributes, sub_query)
            else:
                # content = "attributes.new_attribute_not_exist"
                err_msg = u"Failed to extract cumstom set attribute from teardown hooks! => {}\n".format(field)
                err_msg += u"response set attributes: {}\n".format(attributes)
                raise exceptions.TeardownHooksFailure(err_msg)

        # others
        else:
            err_msg = f"""
            从响应中提取属性数据失败 ! => {field}
            可用的响应属性: status_code、cookies、elapsed、headers、content、text、json、encoding、ok、reason、url
            如果要在teardown_hooks中设置属性，请参考以下示例:
            response.new_attribute = 'new_attribute_value'
            """
            raise exceptions.ParamsError(err_msg)

    def extract_field(self, field, variable_data=None):
        """ 从响应数据中提取数据 """
        if not isinstance(field, basestring):
            err_msg = f"无效的提取器 => {field}\n"
            raise exceptions.ParamsError(err_msg)

        # 判断是否能被正则编译，如果能被正则编译，则用正则提取方式
        if text_extractor_regexp_compile.match(field):
            value = self._extract_field_with_regex(field)
        else:
            value = self._extract_field_with_delimiter(field, variable_data)

        return value

    def extract_response(self, session_context, extractors):
        """ 从响应信息中提取值，并储存到 OrderedDict对象
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
        extract_binds_order_dict = utils.list_to_dict(extractors)
        # 提取数据
        for extract_key, expression in extract_binds_order_dict.items():

            functions = extract_functions(expression)
            if functions:  # 有嵌套自定义函数，先执行提取，再执行自定义函数
                # 提取自定义函数 {'func_name': 'add', 'args': ['content.data'], 'kwargs': {}}
                extract_function_data = parse_function(functions[0])

                # 执行数据提取
                extract_arg_data = []  # arg
                for arg in extract_function_data.get('args', []):
                    # 判断是常量还是自定义变量，如果是自定义变量，则替换
                    variable = extract_variables(arg)
                    if variable:
                        extract_arg_data.append(get_mapping_variable(variable[0], session_context_variables_mapping))
                    else:
                        if is_const(arg):
                            extract_arg_data.append(str(arg))
                        else:
                            extract_arg_data.append(self.extract_field(arg) if is_extract_expression(arg) else arg)


                extract_kwarg_data = {}  # kwarg
                for key, value in extract_function_data.get('kwargs', {}).items():
                    # 判断是常量还是自定义变量，如果是自定义变量，则替换
                    variable = extract_variables(value)
                    if variable:
                        extract_kwarg_data[key] = get_mapping_variable(variable[0], session_context_variables_mapping)
                    else:
                        extract_kwarg_data[key] = self.extract_field(value) if is_extract_expression(value) else value

                # 执行自定义函数
                extract_function_data['args'], extract_function_data['kwargs'] = extract_arg_data, extract_kwarg_data
                result = session_context.FUNCTIONS_MAPPING[extract_function_data['func_name']](
                    *extract_function_data['args'],
                    **extract_function_data['kwargs']
                )
                extracted_variables_mapping[extract_key] = result
                session_context_variables_mapping[extract_key] = result

            else:  # 没有嵌套自定义函数，则直接提取
                if expression.startswith("const"):  # 常量
                    result = expression.split("const.")[1]
                elif expression.startswith("variable"):  # 变量：variable.$data.data 或者 variable.$data
                    variable_expression = expression.split("variable.")[1]
                    variable_expression_split = variable_expression.split(".", 1)
                    if len(variable_expression_split) > 1:  # $data.data
                        variable, extract_expression = variable_expression_split
                        variable_data = extract_variables(variable)[0]
                        result = self.extract_field(
                            f"variable.{extract_expression}",
                            get_mapping_variable(variable_data, session_context_variables_mapping)
                        )
                    else:  # $data
                        variable_data = extract_variables(variable_expression_split[0])[0]
                        result = get_mapping_variable(variable_data, session_context_variables_mapping)
                else:  # 从响应中提取
                    result = self.extract_field(expression)
                extracted_variables_mapping[extract_key] = result
                session_context_variables_mapping[extract_key] = result

        return extracted_variables_mapping
