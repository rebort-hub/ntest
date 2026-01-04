from typing import Optional, List
from pydantic import Field

from ..base_form import BaseForm, ChangeSortForm, PaginationForm, AddUiElementDataForm


class ElementListForm(PaginationForm):
    """ 查询元素信息 """
    page_id: int = Field(..., title="页面id")
    name: Optional[str] = Field(default=None, title="元素名")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {"page_id": self.page_id}
        if self.name:
            filter_dict["name__icontains"] = self.name
        return filter_dict


class GetElementForm(BaseForm):
    """ 获取元素 """
    id: int = Field(..., title="元素id")


class DeleteElementForm(GetElementForm):
    """ 删除元素 """


class AddElementForm(BaseForm):
    """ 添加元素信息的校验 """
    project_id: int = Field(..., title="项目id")
    module_id: int = Field(..., title="模块id")
    page_id: int = Field(..., title="页面id")
    element_list: List[AddUiElementDataForm] = Field(..., title="元素list")


class EditElementForm(BaseForm):
    """ 修改元素信息 """
    id: int = Field(..., title="元素id")
    name: str = Field(..., title="元素名")
    by: str = Field(..., title="定位方式")
    element: str = Field(..., title="定位元素表达式")
    template_device: Optional[int] = Field(default=None, title="元素定位时参照的设备")
    desc: Optional[str] = Field(default=None, title="备注")
    wait_time_out: Optional[int] = Field(default=None, title="等待超时时间")


class ChangeElementByIdForm(BaseForm):
    """ 根据id更新元素 """
    id: int = Field(..., title="元素id")
    by: str = Field(..., title="定位方式")
    element: str = Field(..., title="定位元素表达式")
