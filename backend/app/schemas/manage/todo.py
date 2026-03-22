from typing import List
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm


class GetTodoForm(BaseForm):
    id: int = Field(..., title="数据id")


class ChangeStatusForm(GetTodoForm):
    status: str = Field(..., title="状态")


class TodoForm(BaseForm):
    title: str = Field(..., title="任务title")
    detail: str = Field(..., title="任务详情")


class AddTodoForm(BaseForm):
    """ 添加数据 """
    data_list: List[TodoForm] = Field(..., title="新增数据")


class ChangeTodoForm(GetTodoForm, TodoForm):
    """ 修改数据 """
