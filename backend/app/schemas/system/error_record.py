from typing import Optional
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm


class GetSystemErrorRecordList(PaginationForm):
    url: Optional[str] = Field(default=None, title="请求地址")
    method: Optional[str] = Field(default=None, title="请求方法")
    request_user: Optional[str] = Field(default=None, title="发起请求用户")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {}
        if self.url:
            filter_dict["url__icontains"] = self.url
        if self.method:
            filter_dict["method"] = self.method
        if self.method:
            filter_dict["method"] = self.method
        if self.request_user:
            filter_dict["create_user"] = self.request_user

        return filter_dict

class GetSystemErrorRecordForm(BaseForm):
    id: int = Field(..., title="数据id")
