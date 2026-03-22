from typing import Optional, List
from pydantic import Field

from ..base_form import PaginationForm, BaseForm, ChangeSortForm
from app.schemas.enums import WebHookTypeEnum


class GetWebHookListForm(PaginationForm):
    """ 获取webhook列表 """
    name: Optional[str] = Field(default=None, title="webhook名字")
    addr: Optional[str] = Field(default=None, title="webhook地址")
    webhook_type: Optional[str] = Field(default=None, title="webhook类型")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {}
        if self.name:
            filter_dict["name__icontains"] = self.name
        if self.addr:
            filter_dict["addr__icontains"] = self.addr
        if self.webhook_type:
            filter_dict["webhook_type"] = self.webhook_type
        return filter_dict


class GetWebHookForm(BaseForm):
    """ 获取webhook校验 """
    id: int = Field(..., title="数据id")


class WebHookForm(BaseForm):
    """ webhook校验 """
    name: str = Field(..., title="webhook名字")
    addr: str = Field(..., title="webhook地址")
    webhook_type: WebHookTypeEnum = Field(..., title="webhook类型，钉钉、企业微信、飞书")
    secret: Optional[str] = Field(default=None, title="webhook秘钥")
    desc: Optional[str] = Field(default=None, title="备注")


class PostWebHookForm(BaseForm):
    """ 新增webhook校验 """
    data_list: List[WebHookForm] = Field(..., title="webhook list")


class PutWebHookForm(GetWebHookForm, WebHookForm):
    """ 修改webhook校验 """
