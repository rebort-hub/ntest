import re
from typing import Optional, List
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm


class GetRunEnvListForm(PaginationForm):
    """ 获取环境列表 """
    name: Optional[str] = Field(default=None, title="环境名")
    code: Optional[str] = Field(default=None, title="环境code")
    group: Optional[str] = Field(default=None, title="环境分组")
    create_user: Optional[str] = Field(default=None, title="创建者")
    business_id: Optional[int] = Field(default=None, title="业务线")
    project_id: Optional[int] = Field(default=None, title="服务id")
    test_type: Optional[str] = Field(default=None, title="测试类型", description="与project_id搭配")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        user, filter_dict, validate_filter = kwargs.get("user"), {}, kwargs.get("validate_filter")

        if self.business_id:
            filter_dict.update(validate_filter)
        if self.name:
            filter_dict["name__icontains"] = self.name
        if self.code:
            filter_dict["code__icontains"] = self.code
        if self.group:
            filter_dict["group__icontains"] = self.group
        if self.create_user:
            filter_dict["create_user"] = int(self.create_user)
        return filter_dict


class GetRunEnvForm(BaseForm):
    """ 获取环境表单校验 """
    id: int = Field(..., title="环境id")


class RunEnvForm(BaseForm):
    """ 新增环境表单校验 """
    name: str = Field(..., title="环境名", min_length=2)
    code: str = Field(..., title="环境code", min_length=2)
    group: str = Field(..., title="环境分组", min_length=2)
    desc: Optional[str] = Field(default=None, title="备注")


class PostRunEnvForm(BaseForm):
    """ 新增环境表单校验 """
    env_list: List[RunEnvForm] = Field(..., title="环境list")

    async def validate_request(self, *args, **kwargs):
        code_list = []
        for add_env in self.env_list:
            if add_env.code in code_list:
                raise ValueError(f"环境code【{add_env.code}】重复")
            if re.match('^[a-zA-Z][a-zA-Z0-9_\\.]+$', add_env.code) is None:
                raise ValueError(f"环境code【{add_env.code}】错误，正确格式为：英文字母开头+英文字母/下划线/数字")
            code_list.append(add_env.code)


class PutRunEnvForm(GetRunEnvForm, RunEnvForm):
    """ 修改环境表单校验 """


class EnvToBusinessForm(BaseForm):
    """ 批量管理环境与业务线的关系 绑定/解除绑定 """
    env_list: list = Field(..., title="环境")
    business_list: list = Field(..., title="业务线")
    command: str = Field(..., title="操作类型")  # add、delete
