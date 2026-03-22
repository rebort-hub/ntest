from typing import Optional
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm


class GetJobRunLogList(PaginationForm):
    func_name: Optional[str] = Field(..., title="方法名")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {}
        if self.func_name:
            filter_dict["func_name"] = self.func_name

        return filter_dict

class GetJobLogForm(BaseForm):
    """ 获取job信息 """
    id: int = Field(..., title="数据id")


class GetJobForm(BaseForm):
    """ 获取job信息 """
    task_code: str = Field(..., title="job code")


class EnableJobForm(BaseForm):
    """ 新增job信息 """
    func_name: str = Field(..., title="job方法")


class DisableJobForm(EnableJobForm):
    """ 禁用job """


class RunJobForm(EnableJobForm):
    """ 执行job """