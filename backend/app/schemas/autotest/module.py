from typing import Optional, List
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm


class GetModuleTreeForm(BaseForm):
    project_id: int = Field(..., title="服务id")


class FindModuleForm(GetModuleTreeForm, PaginationForm):
    """ 查找模块 """
    name: Optional[str] = Field(default=None, title="模块名")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {"project_id": self.project_id}
        if self.name:
            filter_dict["name__icontains"] = self.name
        return filter_dict


class AddModuleForm(GetModuleTreeForm):
    """ 添加模块的校验 """
    data_list: List[str] = Field(..., title="模块名list")
    parent: Optional[int] = Field(default=None, title="父级id")


class GetModuleForm(BaseForm):
    """ 获取模块信息 """
    id: int = Field(..., title="模块id")


class EditModuleForm(GetModuleForm, GetModuleTreeForm):
    """ 修改模块的校验 """
    name: str = Field(..., title="模块名")
    parent: Optional[int] = Field(default=None, title="父级id")
