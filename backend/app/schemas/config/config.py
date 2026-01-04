from typing import Optional, List
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm


class GetConfigTypeListForm(PaginationForm):
    """ 获取配置类型列表 """
    name: Optional[str] = Field(default=None, title="类型名")
    create_user: Optional[int] = Field(default=None, title="创建者")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {}
        if self.name:
            filter_dict["name__icontains"] = self.name
        if self.create_user:
            filter_dict["create_user"] = int(self.create_user)
        return filter_dict


class GetConfigTypeForm(BaseForm):
    """ 配置类型id存在 """
    id: int = Field(..., title="配置类型id")


class ConfigTypeForm(BaseForm):
    """ 配置类型表单校验 """
    name: str = Field(..., title="配置类型名")
    desc: Optional[str] = Field(default=None, title="备注")


class PostConfigTypeForm(BaseForm):
    """ 新增配置类型表单校验 """
    data_list: List[ConfigTypeForm] = Field(..., title="配置类型list")


class PutConfigTypeForm(GetConfigTypeForm, ConfigTypeForm):
    """ 修改配置类型表单校验 """


class FindConfigForm(PaginationForm):
    """ 查找配置form """
    type: Optional[str] = Field(default=None, title="配置类型")
    name: Optional[str] = Field(default=None, title="配置名")
    value: Optional[str] = Field(default=None, title="配置值")
    create_user: Optional[str] = Field(default=None, title="创建者")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {}
        if self.type:
            filter_dict["type"] = int(self.type)
        if self.name:
            filter_dict["name__icontains"] = self.name
        if self.value:
            filter_dict["value__icontains"] = self.value
        if self.create_user:
            filter_dict["create_user"] = int(self.create_user)
        return filter_dict


class GetConfigForm(BaseForm):
    """ 获取配置 """
    id: Optional[int] = Field(default=None, title="配置id")
    code: Optional[str] = Field(default=None, title="配置名")


class GetSkipIfConfigForm(BaseForm):
    """ 获取跳过类型配置 """
    test_type: str = Field(..., title="测试类型")
    type: str = Field(..., title="跳过类型")


class GetFindElementByForm(BaseForm):
    """ 获取定位方式数据源 """
    test_type: str = Field(..., title="测试类型")


class GetConfigByIdForm(BaseForm):
    """ 获取配置表单校验 """
    id: int = Field(..., title="配置id")


class PostConfigForm(BaseForm):
    """ 新增配置表单校验 """
    name: str = Field(..., title="配置名")
    value: str = Field(..., title="配置值")
    type: str = Field(..., title="配置类型")
    desc: Optional[str] = Field(default=None, title="备注")


class PutConfigForm(GetConfigByIdForm, PostConfigForm):
    """ 修改配置表单校验 """


class ValidatorForm(BaseForm):
    """ 断言表单 """
    key: str = Field(..., title="实际结果表达式")
    value: str = Field(..., title="预期结果表达式")
    status: int = Field(..., title="启用1、禁用0")
    data_type: str = Field(..., title="数据类型")
    data_source: str = Field(..., title="数据源")
    validate_type: str = Field('data', title="断言类型，数据、ui")
    validate_method: str = Field('相等', title="断言方法映射")


class AddApiDefaultValidatorConfigForm(BaseForm):
    """ 添加 api_default_validator 的配置项
        {
        "label": "code=0",
        "value": {"key": "code", "value": "0", "status": 1, "data_type": "int", "data_source": "content", "validate_type": "data", "validate_method": "相等"}
        }
    """
    label: str = Field(..., title="断言方式描述，如 code=0")
    value: ValidatorForm
