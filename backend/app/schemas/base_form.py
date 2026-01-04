import json
import re

import httpx
import validators
from typing import Optional, Union
from pydantic import BaseModel as pydanticBaseModel, Field

from utils.client.test_runner.parser import extract_variables, parse_function, extract_functions
from utils.util.json_util import JsonUtil

class CurrentUserModel(pydanticBaseModel):
    """ 根据token解析出来的用户信息，用于在后续处理接口逻辑的时候使用 """
    # 可能是没登录的
    id: Optional[int] = None
    account: Optional[str] = None
    name: Optional[str] = None
    business_list: Optional[list] = None
    api_permissions: Optional[list] = None


class ParamModel(pydanticBaseModel):
    key: Union[str, None] = None
    value: Union[str, None] = None


class HeaderModel(ParamModel):
    remark: Union[str, None] = None


class DataFormModel(HeaderModel):
    data_type: Union[str, None] = None


class VariablesModel(DataFormModel):
    pass


class ExtractModel(HeaderModel):
    value: Optional[Union[str, int, None]] = None
    status: Union[int, None] = None
    data_source: Union[str, None] = None
    extract_type: Union[str, None] = None
    update_to_header: Optional[Union[bool, int, None]] = None


class ValidateModel(HeaderModel):
    status: Union[int, None] = None
    validate_type: Union[str, None] = None
    data_type: Union[str, None] = None
    data_source: Union[str, None] = None
    validate_method: Union[str, None] = None


class SkipIfModel(HeaderModel):
    status: Optional[Union[int, None]] = None
    expect: Union[str, int, None] = None
    data_type: Union[str, None] = None
    skip_type: Union[str, None] = None
    comparator: Union[str, None] = None
    check_value: Union[str, None] = None
    data_source: Union[str, None] = None


class ApiListModel(pydanticBaseModel):
    name: str = Field(..., title="接口名字")
    method: str = Field(..., title="请求方法")
    addr: str = Field(..., title="接口地址")


class AddCaseDataForm(pydanticBaseModel):
    name: str = Field(..., title="名字")
    desc: str = Field(..., title="描述")


class AddPageDataForm(pydanticBaseModel):
    name: str = Field(..., title="名字")
    desc: Optional[str] = Field(default=None, title="描述")


class AddUiElementDataForm(pydanticBaseModel):
    name: str = Field(..., title="名字")
    by: str = Field(..., title="定位方式")
    element: str = Field(..., title="定位表达式")
    wait_time_out: Optional[int] = Field(default=5, title="元素等待超时时间")
    template_device: Optional[int] = Field(default=None, title="定位元素时参照的手机")


class BaseForm(pydanticBaseModel, JsonUtil):
    """ 基类数据模型 """

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return self.__dict__.get(item, None)

    def get_update_data(self, user_id=None):
        """ 获取更新的数据 """
        data = self.model_dump()  # Pydantic v2 使用 model_dump() 替代 dict()
        if "num" in data: data.pop("num")
        if user_id: data["update_user"] = user_id
        if "id" in data: data.pop("id")
        return data

    @classmethod
    def is_admin(cls, api_permissions: list):
        """ 管理员权限 """
        return 'admin' in api_permissions

    @classmethod
    def is_not_admin(cls, api_permissions: list):
        """ 非管理员权限 """
        return cls.is_admin(api_permissions) is False

    @classmethod
    def validate_is_true(cls, data, msg):
        """ 判断为真 """
        if not data:
            raise ValueError(msg)

    def validate_email(self, email_server, email_from, email_to):
        """ 发件邮箱、发件人、收件人、密码 """
        if not email_server:
            raise ValueError("选择了要邮件接收，则发件邮箱服务器必填")

        if not email_to or not email_from:
            raise ValueError("选择了要邮件接收，则发件人、收件人必须有值")

        # 改为选用户后，不校验邮箱格式
        # # 校验发件邮箱
        # if email_from and not validators.email(email_from.strip()):
        #     raise ValueError(f"发件人邮箱【{email_from}】格式错误")
        #
        # # 校验收件邮箱
        # for mail in email_to:
        #     mail = mail.strip()
        #     if mail and not validators.email(mail):
        #         raise ValueError(f"收件人邮箱【{mail}】格式错误")

    def validate_func(self, func_container: dict, content: str, message=""):

        functions = extract_functions(content)

        # 使用了自定义函数，但是没有引用函数文件的情况
        if functions and not func_container:
            raise ValueError(f"{message}要使用自定义函数则需引用对应的函数文件")

        # 使用了自定义函数，但是引用的函数文件中没有当前函数的情况
        for function in functions:
            func_name = parse_function(function)["func_name"]
            if func_name not in func_container:
                raise ValueError(f"{message}引用的自定义函数【{func_name}】在引用的函数文件中均未找到")

    def validate_is_regexp(self, regexp):
        """ 校验字符串是否为正则表达式 """
        return re.compile(r".*\(.*\).*").match(regexp)

    def validate_variable(self, variables_container: dict, content: str, message=""):
        """ 引用的变量需存在 """
        for variable in extract_variables(content):
            if variable not in variables_container:
                raise ValueError(f"{message}引用的变量【{variable}】不存在")

    def validate_header_format(self, content: list):
        """ 头部信息，格式校验 """
        for index, data in enumerate(content):
            title, key, value = f"头部信息设置，第【{index + 1}】行", data.get("key"), data.get("value")
            if not ((key and value) or (not key and not value)):
                raise ValueError(f"{title}，要设置头部信息，则key和value都需设置")

    def validate_variable_format(self, content: list, msg_title='自定义变量'):
        """ 自定义变量，格式校验 """
        for index, data in enumerate(content):
            title = f"{msg_title}设置，第【{index + 1}】行"
            key, value, data_type = data.get("key"), data.get("value"), data.get("data_type")

            # 检验数据类型
            if key:
                if not data_type or not value or not data.get("remark"):
                    raise ValueError(f"{title}，要设置{msg_title}，则【key、数据类型、备注】都需设置")

                if self.validate_data_format(value, data_type) is False:
                    raise ValueError(f"{title}，{msg_title}值与数据类型不匹配")

    def validate_data_format(self, value, data_type):
        """ 校验数据格式 """
        try:
            if data_type in ["variable", "func", "str", "file", "True", "False"]:
                pass
            elif data_type == "json":
                self.dumps(self.loads(value))
            elif data_type == "data_driver_list":
                list(value)
            else:  # python数据类型
                eval(f"{data_type}({value})")
        except Exception as error:
            return False

    def validate_data_validates(self, validate_data, row_msg):
        """ 校验断言信息，全都有才视为有效 """
        data_source, key = validate_data.get("data_source"), validate_data.get("key")
        validate_method = validate_data.get("validate_method")
        data_type, value = validate_data.get("data_type"), validate_data.get("value")

        if (not data_source and not data_type) or (
                data_source and not key and validate_method and data_type and not value):
            return
        elif (data_source and not data_type) or (not data_source and data_type):
            raise ValueError(f"{row_msg}若要进行断言，则数据源、预期结果、数据类型需同时存在")

        else:  # 有效的断言
            # 实际结果，选择的数据源为正则表达式，但是正则表达式错误
            if data_source == "regexp" and not self.validate_is_regexp(key):
                raise ValueError(f"{row_msg}正则表达式【{key}】错误")

            if not validate_method:  # 没有选择断言方法
                raise ValueError(f"{row_msg}请选择断言方法")

            if value is None:  # 要进行断言，则预期结果必须有值
                raise ValueError(f"{row_msg}预期结果需填写")

            self.validate_data_type_(row_msg, data_type, value)  # 校验预期结果的合法性

    def validate_page_validates(self, validate_data, row_msg):
        validate_method, data_source = validate_data.get("validate_method"), validate_data.get("data_source")
        data_type, value = validate_data.get("data_type"), validate_data.get("value")

        if validate_method and data_source and data_type and value:  # 都存在
            self.validate_data_type_(row_msg, data_type, value)  # 校验预期结果
        elif validate_method and not data_source and data_type and not value:  # 仅断言方式和数据类型存在
            return
        elif not validate_method and not data_source and not data_type and not value:  # 所有数据都不存在
            return
        else:
            raise ValueError(f"{row_msg}，数据异常，请检查")

    def validate_base_validates(self, data):
        """ 校验断言信息，全都有才视为有效 """
        for index, validate_data in enumerate(data):
            if validate_data.get("status") == 1:
                row_msg = f"断言，第【{index + 1}】行，"
                validate_type = validate_data.get("validate_type")

                if not validate_type:  # 没有选择断言类型
                    raise ValueError(f"{row_msg}请选择断言类型")

                if validate_type == 'data':  # 数据断言
                    self.validate_data_validates(validate_data, row_msg)
                else:  # 页面断言
                    self.validate_page_validates(validate_data, row_msg)

    @classmethod
    def validate_data_type_(cls, row, data_type, value):
        """ 校验数据类型 """
        if data_type in ["str", "file"]:  # 普通字符串和文件，不校验
            pass
        elif data_type == "variable":  # 预期结果为自定义变量，能解析出变量即可
            if extract_variables(value).__len__() < 1:
                raise ValueError(f"{row}引用的变量表达式【{value}】错误")
        elif data_type == "func":  # 预期结果为自定义函数，校验校验预期结果表达式、实际结果表达式
            # self.validate_func(func_container, value, message=row)  # 实际结果表达式是否引用自定义函数
            pass
        elif data_type == "json":  # 预期结果为json
            try:
                json.dumps(json.loads(value))
            except Exception as error:
                raise ValueError(f"{row}预期结果【{value}】，不可转为【{data_type}】")
        else:  # python数据类型
            try:
                eval(f"{data_type}({value})")
            except Exception as error:
                raise ValueError(f"{row}预期结果【{value}】，不可转为【{data_type}】")

    def validate_api_extracts(self, data):
        """ 校验接口测试数据提取表达式 """
        for index, validate in enumerate(data):
            if validate.get("status") == 1:
                row = f"数据提取，第【{index + 1}】"
                data_source, key, value = validate.get("data_source"), validate.get("key"), validate.get("value")

                if key or data_source:
                    if not key or not data_source or not validate.get("remark"):
                        raise ValueError(f"数据提取第 {row} 行，要设置数据提取，则【key、数据源、备注】都需设置")

                # 实际结果，选择的数据源为正则表达式，但是正则表达式错误
                if key and data_source == "regexp" and value and not self.validate_is_regexp(value):
                    raise ValueError(f"数据提取第 {row} 行，正则表达式【{value}】错误")

    async def validate_appium_server_is_running(self, server_ip, server_port):
        """ 校验appium服务器是否能访问 """
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(url=f'http://{server_ip}:{server_port}', timeout=10)
            if response.status_code >= 500:
                raise
        except Exception as error:
            raise ValueError("设置的appium服务器地址不能访问，请检查")


class ChangeSortForm(BaseForm):
    """ 权限排序校验 """
    id_list: list = Field(..., title="要排序的id列表")
    page_no: int = Field(default=1, title="页数")
    page_size: int = Field(default=10, title="页码")


class PaginationForm(BaseForm):
    """ 分页的模型 """
    page_no: Optional[int] = Field(default=None, title="页数")
    page_size: Optional[int] = Field(default=None, title="页码")
    detail: bool = Field(default=False, title='是否获取详细数据')

    def get_query_filter(self, *args, **kwargs):
        """ 解析分页条件，此方法需重载 """
        return {}

    async def make_pagination(self, db_Model, get_filed: list = [], not_get_filed: list = [], **kwargs):
        """ 执行分页查询 """

        # 有num就用num升序，否则用id降序
        order_by_filed = "num" if "num" in db_Model._meta.fields else "-id"

        # 如果没传指定字段，则默认查全部字段
        if len(get_filed) == 0:
            get_filed = db_Model.filter_not_get_filed(not_get_filed)

        query = db_Model.filter(**self.get_query_filter(**kwargs)).order_by(order_by_filed)
        total = await query.count()

        if self.page_no and self.page_size:
            query = query.offset((int(self.page_no) - 1) * int(self.page_size)).limit(int(self.page_size))

        data = await query.values(*get_filed) if get_filed else await query
        return {"total": total, "data": data}
