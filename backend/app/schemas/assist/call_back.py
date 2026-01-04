from typing import Optional
from pydantic import Field

from ..base_form import PaginationForm, BaseForm, ChangeSortForm


class FindCallBackForm(PaginationForm):
    """ 查找回调记录列表form """
    url: Optional[str] = Field(default=None, title='接口地址')

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {}
        if self.url:
            filter_dict["url__icontains"] = self.url
        return filter_dict

class GetCallBackForm(BaseForm):
    """ 获取回调记录 """
    id: int = Field(title='回调数据id')
