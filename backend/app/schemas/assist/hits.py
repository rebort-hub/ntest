from typing import Optional
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm


class GetHitListForm(PaginationForm):
    """ 获取自动化测试命中问题列表 """
    date: Optional[str] = Field(default=None, title='记录时间')
    hit_type: Optional[str] = Field(default=None, title='问题类型')
    test_type: Optional[str] = Field(default=None, title='测试类型')
    hit_detail: Optional[str] = Field(default=None, title='问题内容')
    report_id: Optional[int] = Field(default=None, title='报告id')

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {}
        if self.date:
            filter_dict["date"] = self.date
        if self.hit_type:
            filter_dict["hit_type"] = self.hit_type
        if self.test_type:
            filter_dict["test_type"] = self.test_type
        if self.report_id:
            filter_dict["report_id"] = self.report_id
        if self.hit_detail:
            filter_dict["hit_detail__icontains"] = self.hit_detail
        return filter_dict


class GetHitForm(BaseForm):
    """ 获取自定义自动化测试命中问题 """
    id: int = Field(..., title="数据id")


class CreatHitForm(BaseForm):
    """ 创建自定义自动化测试命中问题 """
    date: str = Field(..., title='问题触发日期')
    hit_type: str = Field(..., title='问题类型')
    test_type: str = Field(..., title='测试类型')
    hit_detail: str = Field(..., title='问题内容')
    env: str = Field(..., title='环境')
    project_id: int = Field(..., title='服务id')
    report_id: int = Field(..., title='测试报告id')
    desc: Optional[str] = Field(default=None, title='描述')

    async def validate_request(self, *args, **kwargs):
        self.date = self.date[0:10]


class EditHitForm(GetHitForm, CreatHitForm):
    """ 修改自定义自动化测试命中问题 """


class DeleteHitForm(BaseForm):
    """ 删除 """
    id_list: list = Field(..., title="问题记录id list")
