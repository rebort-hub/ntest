# -*- coding: utf-8 -*-
from utils.util.file_util import FileUtil
from utils.util.json_util import JsonUtil
from config import assert_mapping, ui_assert_mapping_dict
from utils.client.test_runner.parser import extract_functions, parse_function, extract_variables


class FormatModel(JsonUtil):

    def parse_list_data(self, data_list):
        """ 解析头部参数、params参数
        headers_list:
            [{"key": "x-auth-token", "value": "aaa"}, {"key": null, "value": null}]
        :return
            {"x-auth-token": "aaa"}
        """
        return {data["key"]: data["value"] for data in data_list if data.get("key") and data.get("value") is not None}

    def parse_variables(self, variables_list):
        """ 解析公用变量
        variables_list:
            [
                {"key":"auto_test_token","remark":"token","value":"eyJhbGciOiJIUzI1NiJ9"},
                {"key":"rating_amount","remark":"申请金额","value":"500000"}
            ]
        :return
            {"auto_test_token": "eyJhbGciOiJIUzI1NiJ9", "rating_amount": "500000"}
        """
        data = {
            "data_driver_dict": {
                "key": "",
                "value": []
            }
        }
        for v in variables_list:
            if v.get("key") is not None and v.get("value") is not None:
                if v.get("data_type", "str") != "data_driver_list":
                    data[v["key"]] = self.build_data(v.get("data_type", "str"), v["value"])
                else: # 用例的数据驱动，单独存放，后续解析用例的时候使用
                    data["data_driver_dict"]["key"] = v["key"]
                    data["data_driver_dict"]["value"] = self.build_data(v.get("data_type", "str"), v["value"])
        return data

        # return {
        #     v["key"]: self.build_data(v.get("data_type", "str"), v["value"])
        #     for v in variables_list if v.get("key") is not None and v.get("value") is not None
        # }

    def parse_extracts(self, extracts_list, is_api=True):
        """ 解析要提取的参数
        extracts_list:
            [
                {"key": "project_id", "value": "content.data.id", "remark": "服务id", "update_to_header": True},
                {"key": "project_id1", "value": "content.data.id", "remark": "服务id", "update_to_header": False}
            ]
        return:
            {
                "extractors": [
                    {"project_id": "content.data.id"},
                    {"project_id1": "content.data.id"},
                ],
                "update_to_header_filed_list": ["project_id"]
            }
        """
        if is_api:
            parsed = {
                "extractors": [],
                "update_to_header_filed_list": []
            }
            for extract in extracts_list:
                if extract.get("status") == 1:
                    if extract.get("key") and extract.get("data_source"):  # 有设置key和数据源的，则视为有效提取表达式
                        parsed["extractors"].append({
                            extract["key"]: self.build_extract_expression(extract.get("data_source"), extract["value"])
                        })
                        if extract.get("update_to_header"):
                            parsed["update_to_header_filed_list"].append(extract["key"])
            return parsed
        else:
            """ 解析ui自动化要提取的参数，key、element、extract_type均有值才有效
            value: 元素id
            extracts_list:
                [
                    {"key": "project_id", "value": "1", "extract_type": "123"},
                    {"key": "project_id1", "value": "", "extract_type": "123"},
                    {"key": "project_id2", "value": "1", "extract_type": ""},
                    {"key": "", "value": "1", "extract_type": "123"},
                    {"key": "", "value": "", "extract_type": ""},
                ]
            return:
                [{"key": "project_id", "element": "id", "extract_type": "123"}]
            """
            extractor_list = []
            for extract in extracts_list:
                extract_type = extract.get("extract_type")
                if extract.get("status") and extract.get("key") and extract_type:
                    extract_type_lower = extract_type.lower()
                    if ("cookie" in extract_type_lower
                            or "session_storage" in extract_type_lower
                            or "local_storage" in extract_type_lower
                            or "title" in extract_type_lower):
                        extractor_list.append(extract)
                    else:
                        if extract.get("value"):
                            extractor_list.append(extract)
            return extractor_list

    def parse_validates(self, validates_list):
        """ 解析断言
        validates:
            [
                {
                     "validate_type": "data/page",
                    "data_source": "content",
                    "key": "status",
                    "validate_method": "相等",
                    "data_type": "int",
                    "value": "200",
                    "remark": null
                }
            ]
        return:
            [{"equals": ["1", "content.message"]}]
        """
        parsed_validate = []
        for validate in validates_list:
            if validate.get("status") == 1:
                validate_method = validate.get("validate_method")
                data_source, key = validate.get("data_source"), validate.get("key")
                data_type, value = validate.get("data_type"), validate.get("value")

                if validate.get("validate_type") == 'data':  # 数据校验
                    if data_source and data_type and validate_method and value:
                        parsed_validate.append({
                            assert_mapping[validate_method]: [
                                self.build_actual_result(data_source, key),  # 实际结果
                                self.build_data(data_type, value),  # 预期结果
                                validate_method  # 断言方法的文本，用于渲染报告
                            ]
                        })
                else:  # 页面校验
                    if data_source and validate_method and data_type and value:
                        # 根据执行方法文字描述替换成具体的执行方法
                        validate["validate_method"] = ui_assert_mapping_dict[validate_method]
                        parsed_validate.append(validate)

        return parsed_validate

    def build_data(self, data_type, value):
        """ 根据数据类型解析数据 """
        if data_type in ["variable", "func", "str"]:
            return value
        elif data_type == "json":
            return self.dumps(self.loads(value))
        elif data_type in ["None", "True", "False"]:
            return eval(data_type)
        elif data_type == "data_driver_list":
            return eval(f'list({value})')
        else:  # python数据类型
            return eval(f'{data_type}({value})')

    def build_actual_result(self, data_source, key):
        """ 生成实际结果表达式 """
        if data_source == "regexp":  # 正则表达式
            return key
        elif data_source in ("other", "variable", "func"):  # 其他数据，常量、自定义函数、自定义变量
            return key
        elif not key:  # 整个指定的响应对象
            return data_source
        else:
            return f'{data_source}.{key}'

    def build_extract_expression(self, data_source, key):
        """ 生成数据提取表达式 """

        # 自定义函数
        ext_func = extract_functions(key)
        if ext_func:  # 自定义函数
            return self.build_func_expression(ext_func, data_source)
        elif data_source == "regexp":  # 正则表达式
            return key
        elif not key:  # 整个指定的响应对象
            return data_source
        else:  # 自定义函数
            return f'{data_source}.{key}'

    def build_func_expression(self, ext_func, data_source):
        """ 解析自定义函数的提取表达式，并生成新的表达式 """
        func = parse_function(ext_func[0])
        func_name, args, kwargs = func["func_name"], func["args"], func["kwargs"]

        args_and_kwargs = []
        # 处理args参数
        for arg in args:
            # 如果是自定义变量则不改变, 如果不是，则把数据源加上
            if extract_variables(arg).__len__() >= 1:
                args_and_kwargs.append(arg)
            else:
                # 有可能是常量
                try:
                    eval(str(arg))
                    args_and_kwargs.append(str(arg))
                except:
                    args_and_kwargs.append(f'{data_source}.{arg}')

        # 处理kwargs参数
        for kw_key, kw_value in kwargs.items():
            # 如果是自定义变量或者数据源是func则不改变, 如果不是，则把数据源加上
            if extract_variables(kw_value).__len__() >= 1 or data_source == "func":
                args_and_kwargs.append(f'{kw_key}={kw_value}')
            else:
                args_and_kwargs.append(f'{kw_key}={data_source}.{kw_value}')

        return "${" + f'{func_name}({",".join(args_and_kwargs)})' + "}"

    def parse_skip_if(self, skip_if_list, skip_on_fail=0):
        """ 判断 skip_if 是否要执行 """
        data_list = []
        for skip_if in skip_if_list:
            if skip_if and skip_if.get("status") == 1 and skip_if.get("expect"):
                if skip_if.get("data_source") not in ["run_env", "run_server", "run_device"]:  # 常规数据校验
                    skip_if["expect"] = self.build_data(skip_if["data_type"], skip_if["expect"])
                skip_if["comparator_str"] = skip_if["comparator"]
                skip_if["comparator"] = assert_mapping[skip_if["comparator"]]
                data_list.append(skip_if)

        if skip_on_fail == 1:  # 如果设置了失败则跳过，则自动在步骤的跳过条件加上
            data_list.insert(0, {
                'skip_type': 'or',
                'data_source': 'variable',
                'check_value': '$case_run_result',
                'comparator': '_01equals',
                'comparator_str': '相等',
                'data_type': 'str',
                'expect': 'fail'
            })

        return data_list

    def parse_form_data(self, form_data_list):
        """ 解析form参数 """
        string, files = {}, {}
        for data in form_data_list:
            if data.get("key"):
                # 上传文件，防止内存中有大对象，先把名字存下来，真正发请求的时候再读取文件
                if data["data_type"] == "file":
                    files.update({data["key"]: data["value"]})
                else:  # 其他数据类型
                    string.update({data["key"]: self.build_data(data.get("data_type"), data.get("value"))})
        return string, files

    def parse_body(self, kwargs):
        """ 根据请求体数据类型解析请求体 """
        if self.body_type in ["json", "raw"]:
            self.data_json = kwargs.get("data_json", {})
        elif self.body_type in ["form", "data"]:
            self.data_form, self.data_file = self.parse_form_data(kwargs.get("data_form", {}))
        elif self.body_type == "urlencoded":
            self.data_form = kwargs.get("data_urlencoded", {})
            self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        elif self.body_type in ["xml", "text"]:
            self.data_form = kwargs.get("data_text", "")

    def parse_send_keys(self, send_keys):
        """ 解析输入内容 """
        return FileUtil.build_ui_test_file_path(send_keys) if send_keys and "_is_upload" in send_keys else send_keys


class ProjectModel(FormatModel):
    """ 格式化服务信息 """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.script_list = kwargs.get("script_list")
        self.host = kwargs.get("host")
        self.variables = self.parse_variables(kwargs.get("variables", {}))
        self.headers = self.parse_list_data(kwargs.get("headers", {}))  # 接口自动化字段
        self.app_package = kwargs.get("app_package")  # app自动化字段
        self.app_activity = kwargs.get("app_activity")  # app自动化字段


class ApiModel(FormatModel):
    """ 格式化接口信息 """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.time_out = kwargs.get("time_out")
        self.method = kwargs.get("method")
        self.params = self.parse_list_data(kwargs.get("params", {}))
        self.addr = kwargs.get("addr").split("?")[0] if self.params else kwargs.get("addr") # 同时有 params 和 queryString，以 params为准
        self.headers = self.parse_list_data(kwargs.get("headers", {}))
        self.extracts = self.parse_extracts(kwargs.get("extracts", []))
        self.validates = self.parse_validates(kwargs.get("validates", {}))

        # 根据数据类型解析请求体
        self.body_type = kwargs.get("body_type", "json")
        self.data_json, self.data_form, self.data_file = {}, {}, {}
        self.parse_body(kwargs)


class ElementModel(FormatModel):
    """ 格式化元素信息 """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.by = kwargs.get("by")
        self.element = kwargs.get("element")
        self.template_device = kwargs.get("template_device")
        self.wait_time_out = kwargs.get("wait_time_out")
        self.project_id = kwargs.get("project_id")


class CaseModel(FormatModel):
    """ 格式化用例信息 """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.variables = self.parse_variables(kwargs.get("variables", {}))
        self.skip_if = self.parse_skip_if(kwargs.get("skip_if"))
        self.run_times = kwargs.get("run_times")
        self.suite_id = kwargs.get("suite_id")
        self.headers = self.parse_list_data(kwargs.get("headers", {}))  # 接口自动化字段

    def get_attr(self):
        return {
            "id": self.id,
            "name": self.name,
            "variables": self.variables,
            "skip_if": self.skip_if,
            "run_times": self.run_times,
            "headers": self.headers,
            "suite_id": self.suite_id
        }


class StepModel(FormatModel):
    """ 格式化步骤信息 """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.run_times = kwargs.get("run_times")
        self.up_func = kwargs.get("up_func", [])
        self.down_func = kwargs.get("down_func", [])
        self.skip_if = self.parse_skip_if(kwargs.get("skip_if"), kwargs.get("skip_on_fail", 1))
        self.data_driver = kwargs.get("data_driver", {})
        self.quote_case = kwargs.get("quote_case", {})
        self.case_id = kwargs.get("case_id")
        self.project_id = kwargs.get("project_id")

        # 接口自动化
        self.time_out = kwargs.get("time_out")
        self.allow_redirect = kwargs.get("allow_redirect")
        self.replace_host = kwargs.get("replace_host")
        self.headers = self.parse_list_data(kwargs.get("headers", {}))
        self.params = self.parse_list_data(kwargs.get("params", {}))
        self.api_id = kwargs.get("api_id")
        self.body_type = kwargs.get("body_type", "json")
        self.pop_header_filed = kwargs.get("pop_header_filed", [])
        self.data_json, self.data_form, self.data_file = {}, {}, {}
        self.parse_body(kwargs)

        # UI自动化
        self.wait_time_out = kwargs.get("wait_time_out")
        self.execute_type = kwargs.get("execute_type")
        self.send_keys = self.parse_send_keys(kwargs.get("send_keys"))
        self.extracts = kwargs.get("extracts", [])
        self.page_id = kwargs.get("page_id")
        self.element_id = kwargs.get("element_id")

        self.validates = self.parse_validates(kwargs.get("validates", {}))
        self.extracts = self.parse_extracts(kwargs.get("extracts", []), self.api_id)
