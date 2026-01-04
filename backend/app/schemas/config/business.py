from typing import Optional
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm
from app.schemas.enums import ReceiveTypeEnum, BusinessLineBindEnvTypeEnum


class FindBusinessLineForm(PaginationForm):
    """ 查找脚本form """
    code: Optional[str] = Field(default=None, title="业务线code")
    name: Optional[str] = Field(default=None, title="业务线名")
    getAll: Optional[int] = Field(default=None, title="获取所有业务线，需管理员权限")
    create_user: Optional[str] = Field(default=None, title="创建者")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        user, filter_dict = kwargs.get("user"), {}
        if self.is_not_admin(user.api_permissions):  # 如果用户不是管理员权限，则只返回当前用户的业务线
            filter_dict["id__in"] = user.business_list
        if self.name:
            filter_dict["name__icontains"] = self.name
        if self.code:
            filter_dict["code__icontains"] = self.code
        if self.create_user:
            filter_dict["create_user"] = int(self.create_user)
        return filter_dict


class GetBusinessForm(BaseForm):
    """ 获取业务线 """
    id: int = Field(..., title="业务线id")


class PostBusinessForm(BaseForm):
    """ 新增业务线表单校验 """
    code: str = Field(..., title="业务线code", min_length=2)
    name: str = Field(..., title="业务线名", min_length=2)
    receive_type: ReceiveTypeEnum = Field(
        ..., title="接收通知类型", description="not_receive:不接收、we_chat:企业微信、ding_ding:钉钉")
    webhook_list: list = Field(..., title="接收通统计知的渠道")
    bind_env: BusinessLineBindEnvTypeEnum = Field(
        ..., title="绑定环境机制", description="auto：新增环境时自动绑定，human：新增环境后手动绑定")
    env_list: list = Field(..., title="业务线要用的环境")
    desc: Optional[str] = Field(default=None, title="备注")

    async def validate_request(self, *args, **kwargs):
        if self.receive_type != "0":
            self.validate_is_true(f"要接收段统计通知，则通知地址必填", self.webhook_list)


class PutBusinessForm(GetBusinessForm, PostBusinessForm):
    """ 修改业务线表单校验 """

    async def validate_request(self, *args, **kwargs):
        if self.receive_type != "0":
            self.validate_is_true(f"要接收段统计通知，则通知地址必填", self.webhook_list)
        return await self.validate_business_is_exist()


class BusinessToUserForm(BaseForm):
    """ 批量管理业务线与用户的关系 绑定/解除绑定 """
    business_list: list = Field(..., title="业务线")
    user_list: list = Field(..., title="用户")
    command: str = Field(..., title="操作类型")  # add、delete
