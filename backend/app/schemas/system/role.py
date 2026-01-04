from typing import Optional
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm

class FindRoleForm(PaginationForm):
    """ 查找角色参数校验 """
    name: Optional[str] = Field(default=None, title="角色名")
    role_id: Optional[int] = Field(default=None, title="权角色id")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        role_id_list, filter_dict = kwargs.get("role_id_list"), {}
        if role_id_list:
            filter_dict["id__in"] = role_id_list
        if self.name:
            filter_dict["name__icontains"] = self.name
        return filter_dict


class GetRoleForm(BaseForm):
    """ 获取具体角色 """
    id: int = Field(..., title="角色id")


class CreateRoleForm(BaseForm):
    """ 创建角色的验证 """
    name: str = Field(..., title="角色名", min_length=2)
    desc: str = Field(..., title="备注", min_length=2)
    extend_role: list = Field(default=[], title="继承角色")
    api_permission: list = Field(default=[], title="后端权限")
    front_permission: list = Field(default=[], title="前端权限")


class EditRoleForm(GetRoleForm, CreateRoleForm):
    """ 编辑角色的校验 """
