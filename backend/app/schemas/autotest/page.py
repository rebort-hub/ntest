from typing import Optional, List
from pydantic import Field

from ..base_form import BaseForm, ChangeSortForm, PaginationForm, AddPageDataForm


class PageListForm(PaginationForm):
    """ 查询页面信息 """
    module_id: int = Field(..., title="模块id")
    name: Optional[str] = Field(default=None, title="模块名")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {"module_id": self.module_id}
        if self.name:
            filter_dict["name__icontains"] = self.name
        return filter_dict


class GetPageForm(BaseForm):
    """ 获取页面 """
    id: int = Field(..., title="页面id")


class AddPageForm(BaseForm):
    """ 添加页面信息的校验 """
    project_id: int = Field(..., title="项目id")
    module_id: int = Field(..., title="模块id")
    page_list: List[AddPageDataForm] = Field(..., title="页面list")


class EditPageForm(GetPageForm):
    """ 修改页面信息 """
    module_id: int = Field(..., title="模块id")
    id: int = Field(..., title="页面id")
    name: str = Field(..., title="页面名")
    desc: Optional[str] = Field(default=None, title="描述")
