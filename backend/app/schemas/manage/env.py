from typing import Optional, List
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm


class GetEnvListForm(PaginationForm):
    business_list: Optional[str] = Field(default=None, title="业务线")
    name: Optional[str] = Field(default=None, title="环境名")
    value: Optional[str] = Field(default=None, title="数据值")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {"source_type": "addr"}
        if self.name:
            filter_dict["name__icontains"] = self.name
        if self.value:
            filter_dict["value__icontains"] = self.value
        if self.business_list:
            filter_dict["business__in"] = self.business_list.split(',')

        return filter_dict


class GetEnvForm(BaseForm):
    """ 数据详情 """
    id: int = Field(..., title="数据id")


class AddEnvDataForm(BaseForm):
    name: Optional[str] = Field(..., title="名字")
    value: Optional[str] = Field(..., title="值")
    password: Optional[str] = Field(..., title="密码")
    desc: Optional[str] = Field(..., title="值")


class AddEnvForm(BaseForm):
    """ 添加数据 """
    business: Optional[int] = Field(..., title="业务线")
    data_list: List[AddEnvDataForm] = Field(..., title="资源数据")

    async def validate_request(self, *args, **kwargs):
        env_data_list = []
        for index, data in enumerate(self.data_list):
            data = data.dict()
            data["source_type"], data["business"] = 'addr', self.business
            env_data_list.append(data)
        return env_data_list


class ChangeEnvForm(GetEnvForm):
    """ 修改数据 """
    business: Optional[int] = Field(..., title="业务线")
    name: str = Field(..., title="资源名字")
    value: str = Field(..., title="资源对应的值")
    desc: Optional[str] = Field(..., title="描述")


class GetAccountListForm(PaginationForm):
    """ 获取数据列表 """
    business: Optional[list] = Field(default=None, title="业务线")
    name: Optional[str] = Field(default=None, title="环境名")
    parent_id: int = Field(..., title="所属资源id")
    value: Optional[str] = Field(default=None, title="数据值")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {"source_type": "account", "parent": self.parent_id}
        if self.name:
            filter_dict["name__icontains"] = self.name
        if self.value:
            filter_dict["value__icontains"] = self.value
        if self.business:
            filter_dict["business"] = self.business

        return filter_dict


class GetAccountForm(BaseForm):
    """ 数据详情 """
    id: int = Field(..., title="数据id")


class DeleteAccountForm(GetEnvForm):
    """ 删除数据 """


class AddEnvAccountDataForm(BaseForm):
    name: Optional[str] = Field(default=None, title="名字")
    value: Optional[str] = Field(default=None, title="值")
    password: Optional[str] = Field(default=None, title="密码")
    desc: Optional[str] = Field(default=None, title="描述")


class AddAccountForm(BaseForm):
    """ 添加数据 """
    parent: Optional[int] = Field(default=None, title="数据父级id")
    data_list: List[AddEnvAccountDataForm] = Field(..., title="资源数据")

    async def validate_request(self, *args, **kwargs):
        data_list = []
        for index, data in enumerate(self.data_list):
            data = data.dict()
            data["source_type"], data["parent"] = 'account', self.parent
            data_list.append(data)
        return data_list


class ChangeAccountForm(GetEnvForm):
    """ 修改数据 """
    name: str = Field(..., title="资源名字")
    value: str = Field(..., title="资源对应的值")
    password: Optional[str] = Field(default=None, title="密码")
    desc: Optional[str] = Field(default=None, title="描述")
