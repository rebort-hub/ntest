import re
from typing import Optional, Union, List
from pydantic import Field, AnyUrl
import validators

from ...models.system.model_factory import User
from ..base_form import BaseForm, PaginationForm, ValidateModel, HeaderModel, ChangeSortForm


class FindProjectListForm(PaginationForm):
    """ 查找服务form """
    name: Optional[str] = Field(default=None, title="服务名")
    manager: Optional[Union[int, str]] = Field(default=None, title="负责人")
    business_id: Optional[int] = Field(default=None, title="所属业务线")
    create_user: Optional[Union[int, str]] = Field(default=None, title="创建者")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        user, filter_dict = kwargs.get("user"), {}

        if self.business_id:  # 传了业务线id，就获取对应的业务线的服务
            filter_dict["business_id"] = self.business_id
        else:
            if User.is_not_admin(user.api_permissions):  # 非管理员
                filter_dict["business_id__in"] = user.business_list

        if self.name:
            filter_dict["name__icontains"] = self.name
        if self.manager:
            filter_dict["manager"] = self.manager
        if self.business_id:
            filter_dict["business_id"] = self.business_id
        if self.create_user:
            filter_dict["create_user"] = self.create_user
        return filter_dict


class GetProjectForm(BaseForm):
    """ 获取具体服务信息 """
    id: int = Field(..., title="服务id")


class AddProjectForm(BaseForm):
    """ 添加服务参数校验 """
    # name: str = Field(..., min_length=1, max_length=Project.filed_max_length("name"), title="服务名")
    name: str = Field(..., min_length=1, max_length=255, title="服务名")
    manager: int = Field(..., title="负责人")
    business_id: int = Field(..., title="业务线")
    script_list: Optional[list] = Field(default=None, title="要使用的脚本")

    # api自动化测试
    source_type: Optional[str] = Field(default=None, title="服务对应的接口文档地址类型，swagger、apifox")
    source_addr: Optional[AnyUrl] = Field(default=None, title="服务对应的接口文档地址")
    source_id: Optional[int] = Field(default=None, title="服务对应的项目id")

    # app自动化测试
    app_package: Optional[str] = Field(default=None, title="app包名")
    app_activity: Optional[str] = Field(default=None, title="appActivity")
    template_device: Optional[str] = Field(default=None, title="元素定位时参照的设备id")


    def validate_source_addr(self):
        """ 校验接口文档地址 """
        if self.source_addr:
            source_addr = str(self.source_addr)
            self.validate_is_true(f"接口文档地址不正确，请输入正确地址", validators.url(source_addr) is True)
            self.validate_is_true(
                f"接口文档地址不正确，请输入获取接口文档数据的地址，不要输入页面地址",
                "swagger-ui.htm" not in source_addr
            )
            if "/project" in source_addr:  # apifox页面地址
                self.validate_is_true(
                    len(self.parse_source_id()) > 0,
                    "接口文档地址不正确，apifox的项目请输入页面地址即可"
                )
                self.source_id = self.parse_source_id()[-1]

    def parse_source_id(self):
        return re.findall(r"\d+", str(self.source_addr))

    async def validate_request(self, *args, **kwargs):
        self.validate_source_addr()


class EditProjectForm(GetProjectForm, AddProjectForm):
    """ 修改服务参数校验 """

    async def validate_request(self, *args, **kwargs):
        self.validate_source_addr()


class GetEnvForm(BaseForm):
    """ 查找服务环境form """
    project_id: int = Field(..., title="服务id")
    env_id: int = Field(..., title="环境id")


class EditEnvForm(GetEnvForm):
    """ 修改环境 """
    id: int = Field(..., title="环境数据id")
    host: str = Field(..., title="域名")
    variables: List[ValidateModel] = Field(title="变量")
    headers: Optional[List[HeaderModel]] = Field(title="头部信息")

    def validate_variables(self, all_func_name, all_variables):
        """ 公共变量参数的校验
        1.校验是否存在引用了自定义函数但是没有引用脚本文件的情况
        2.校验是否存在引用了自定义变量，但是自定义变量未声明的情况
        """
        variables = [variable.dict() for variable in self.variables]
        self.validate_variable_format(variables)  # 校验格式
        self.validate_func(all_func_name, content=self.dumps(variables))  # 校验引用的自定义函数
        self.validate_variable(all_variables, self.dumps(variables), "自定义变量")  # 校验变量

    def validate_headers(self, all_func_name, all_variables):
        """ 头部参数的校验
        1.校验是否存在引用了自定义函数但是没有引用脚本文件的情况
        2.校验是否存在引用了自定义变量，但是自定义变量未声明的情况
        """
        if self.headers:
            headers = [header.dict() for header in self.headers]
            self.validate_header_format(headers)  # 校验格式
            self.validate_func(all_func_name, content=self.dumps(headers))  # 校验引用的自定义函数
            self.validate_variable(all_variables, self.dumps(headers), "头部信息")  # 校验引用的变量

    async def validate_request(self, *args, **kwargs):
        all_variables = {variable.key: variable.value for variable in self.variables if variable.key}
        self.validate_variables(kwargs["all_func_name"], all_variables)
        self.validate_headers(kwargs["all_func_name"], all_variables)


class SynchronizationEnvForm(BaseForm):
    """ 同步环境form """
    project_id: int = Field(..., title="服务id")
    env_from: int = Field(..., title="环境数据源")
    env_to: list = Field(..., title="要同步到环境")
