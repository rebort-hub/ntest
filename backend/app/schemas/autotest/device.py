from typing import Optional, List

import validators
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm


class GetServerListForm(PaginationForm):
    """ 获取服务器列表 """
    name: Optional[str] = Field(default=None, title="服务器名")
    os: Optional[str] = Field(default=None, title="服务器系统类型")
    ip: Optional[str] = Field(default=None, title="服务器ip")
    port: Optional[str] = Field(default=None, title="服务器端口")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {}
        if self.name:
            filter_dict["name__icontains"] = self.name
        if self.os:
            filter_dict["os"] = self.os
        if self.ip:
            filter_dict["ip"] = self.ip
        if self.port:
            filter_dict["port"] = self.port

        return filter_dict


class GetServerForm(BaseForm):
    """ 校验服务器id已存在 """
    id: int = Field(..., title="服务器id")


class AddAppiumServerDataForm(BaseForm):
    name: str = Field(..., title="服务器名字")
    os: str = Field(..., title="服务器系统类型")
    ip: str = Field(..., title="服务器ip地址")
    port: str = Field(..., title="服务器端口")
    appium_version: str = Field(..., title="服务器端口")

class AddServerForm(BaseForm):
    """ 添加服务器的校验 """
    data_list: List[AddAppiumServerDataForm] = Field(..., title="appium服务器")


class EditServerForm(GetServerForm, AddAppiumServerDataForm):
    """ 修改服务器的校验 """


class GetPhoneListForm(PaginationForm):
    """ 获取运行设备列表 """

    name: Optional[str] = Field(default=None, title="运行设备名")
    os: Optional[str] = Field(default=None, title="运行设备系统类型")
    os_version: Optional[str] = Field(default=None, title="运行设备系统版本")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {}
        if self.name:
            filter_dict["name__icontains"] = self.name
        if self.os:
            filter_dict["os"] = self.os
        if self.os_version:
            filter_dict["os_version__icontains"] = self.os_version

        return filter_dict


class GetPhoneForm(BaseForm):
    """ 获取运行设备 """
    id: int = Field(..., title="运行设备id")


class AddPhoneDataForm(BaseForm):
    name: str = Field(..., title="运行设备名字")
    os: str = Field(..., title="运行设备系统类型")
    os_version: str = Field(..., title="运行设备系统版本")
    device_id: str = Field(..., title="运行设备设备id")
    screen: str = Field(..., title="运行设备系统分辨率")
    extends: dict = Field(..., title="运行设备扩展信息")


class AddPhoneForm(BaseForm):
    """ 添加手机的校验 """
    data_list: List[AddPhoneDataForm] = Field(..., title="手机设备")

class EditPhoneForm(GetPhoneForm, AddPhoneDataForm):
    """ 修改手机的校验 """
