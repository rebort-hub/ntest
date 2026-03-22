from typing import Optional, List
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm
from app.schemas.enums import ApiCaseSuiteTypeEnum


class FindCaseSuite(PaginationForm):
    """ 查找用例集合 """
    name: Optional[str] = Field(default=None, title="用例集名")
    suite_type: Optional[list] = Field(default=None, title="用例集类型")
    project_id: int = Field(..., title="服务id")
    parent: Optional[int] = Field(default=None, title="上级用例集")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {"project_id": self.project_id}
        if self.name:
            filter_dict["name__icontains"] = self.name
        if self.suite_type:
            filter_dict["suite_type__in"] = self.suite_type
        if self.parent:
            filter_dict["parent"] = self.parent
        return filter_dict


class GetCaseSuiteForm(BaseForm):
    """ 获取用例集信息 """
    id: int = Field(..., title="用例集id")


class AddCaseSuiteForm(BaseForm):
    """ 添加用例集的校验 """
    project_id: int = Field(..., title="服务id")
    suite_type: ApiCaseSuiteTypeEnum = Field(
        ..., title="用例集类型",
        description="base: 基础用例集，api: 单接口用例集，process: 流程用例集，make_data: 造数据用例集")
    parent: Optional[int] = Field(default=None, title="父用例集id")
    data_list: List[str] = Field(..., title="用例集名称list")


class EditCaseSuiteForm(GetCaseSuiteForm):
    """ 编辑用例集 """

    project_id: int = Field(..., title="服务id")
    name: str = Field(..., title="用例集名称")
    suite_type: ApiCaseSuiteTypeEnum = Field(
        ..., title="用例集类型",
        description="base: 基础用例集，api: 单接口用例集，process: 流程用例集，assist: 造数据用例集")
    parent: Optional[int] = Field(default=None, title="父用例集id")


class CopyCaseSuiteForm(GetCaseSuiteForm):
    """ 复制用例集 """
    parent: int = Field(..., title="复制后的用例集归属")
    deep: bool = Field(default=True, title="是否递归复制")

class ModuleToCaseSuiteForm(BaseForm):
    """ 模块转用例集 """
    module: int = Field(..., title="模块id")
    parent: int = Field(..., title="复制后的用例集归属")
