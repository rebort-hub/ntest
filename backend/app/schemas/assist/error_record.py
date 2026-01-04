from typing import Optional
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm


class FindErrorForm(PaginationForm):
    """ 查找错误记录列表form """

    name: Optional[str] = Field(default=None, title='函数名')

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {}
        if self.name:
            filter_dict["name__icontains"] = self.name
        return filter_dict


class GetErrorForm(BaseForm):
    id: int = Field(..., title='数据id')
