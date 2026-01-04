from pydantic import Field
from ..base_form import BaseForm, PaginationForm, ChangeSortForm


class GetPullLogListForm(PaginationForm):
    """ 查找swagger拉取记录列表form """
    project_id: int = Field(..., title='服务id')

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """

        return {"project_id": self.project_id}


class GetPullLogForm(BaseForm):
    """ 查找swagger拉取记录 """
    id: int = Field(..., title='数据id')


class SwaggerPullForm(BaseForm):
    """ 查找swagger拉取记录列表form """
    project_id: int = Field(..., title='服务id')
    options: list = Field(..., title='拉取项')
