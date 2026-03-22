from typing import Optional, List
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm


class GetPermissionListForm(PaginationForm):
    """ 查找权限参数校验 """
    name: Optional[str] = Field(default=None, title="权限名")
    source_addr: Optional[str] = Field(default=None, title="权限地址")
    source_type: Optional[str] = Field(default=None, title="权限类型")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {}
        if self.name:
            filter_dict["name__icontains"] = self.name
        if self.source_addr:
            filter_dict["source_addr__icontains"] = self.source_addr
        if self.source_type:
            filter_dict["source_type"] = self.source_type
        return filter_dict


class GetPermissionForm(BaseForm):
    """ 获取具体权限 """
    id: int = Field(..., title="权限id")


class PermissionForm(BaseForm):
    """ 权限的验证 """
    name: str = Field(..., title="权限名")
    desc: Optional[str] = Field(default=None, title="备注")
    source_addr: str = Field(..., title="权限地址")
    source_type: str = Field("front", title="权限类型")
    source_class: str = Field("menu", title="权限分类")


class CreatePermissionForm(BaseForm):
    """ 创建权限的验证 """
    data_list: List[PermissionForm] = Field(..., title="权限列表")


class EditPermissionForm(GetPermissionForm, PermissionForm):
    """ 编辑权限的校验 """
