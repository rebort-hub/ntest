from typing import Optional
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm
from ..enums import ReportStepStatusEnum


class FindReportForm(PaginationForm):
    """ 查询报告 """
    project_id: int = Field(..., title="服务id")
    name: Optional[str] = Field(default=None, title="报告名")
    create_user: Optional[int] = Field(default=None, title="创建人")
    trigger_type: Optional[str] = Field(default=None, title="触发类型")
    run_type: Optional[str] = Field(default=None, title="执行类型")
    is_passed: Optional[int] = Field(default=None, title="是否通过")
    run_env: Optional[list] = Field(default=None, title="运行环境")
    trigger_id: Optional[int] = Field(default=None, title="运行数据id", description="接口id、用例id、任务id")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {"project_id": self.project_id}
        if self.name:
            filter_dict["name__icontains"] = self.name
        if self.create_user:
            filter_dict["create_user"] = self.create_user
        if self.trigger_type:
            filter_dict["trigger_type"] = self.trigger_type
        if self.run_type:
            filter_dict["run_type"] = self.run_type
        if self.is_passed:
            filter_dict["is_passed"] = self.is_passed
        if self.env_list:
            filter_dict["run_env"] = self.run_env
        if self.trigger_id:
            filter_dict["trigger_id__contains"] = self.trigger_id

        return filter_dict


class GetReportForm(BaseForm):
    """ 获取报告 """
    id: int = Field(..., title="报告id")


class DeleteReportForm(BaseForm):
    """ 删除报告 """
    id_list: list = Field(..., title="报告id list")


class GetReportCaseSuiteListForm(PaginationForm):
    """ 获取报告用例集列表 """
    report_id: int = Field(..., title="报告id")


class GetReportCaseListForm(GetReportCaseSuiteListForm):
    """ 获取报告用例列表 """
    get_summary: Optional[bool] = Field(default=None, title="是否获取详情")


class GetReportCaseForm(BaseForm):
    """ 获取报告步骤数据 """
    id: int = Field(..., title="报告用例id")


class GetReportStepListForm(PaginationForm):
    """ 获取报告步骤列表 """
    report_case_id: int = Field(..., title="报告用例id")
    get_summary: Optional[bool] = Field(default=None, title="是否获取详情")


class GetReportStepForm(BaseForm):
    """ 获取报告步骤数据 """
    id: int = Field(..., title="报告步骤id")


class GetReportStepImgForm(BaseForm):
    """ 获取报告步骤截图 """
    report_id: int = Field(..., title="测试报告id")
    report_step_id: int = Field(..., title="报告步骤id")
    img_type: str = Field(..., title="截图类型，before_page, after_page")


class GetReportShowIdForm(BaseForm):
    """ 获取报告状态 """
    batch_id: str = Field(..., title="执行批次id")


class GetReportStatusForm(GetReportShowIdForm):
    """ 获取报告状态 """
    process: int = Field(default=1, title="当前进度")
    status: int = Field(default=1, title="当前进度下的状态")


class ChangeReportStepStatus(BaseForm):
    """ 修改测试报告步骤的状态 stop、pause、resume """
    report_id: Optional[int] = Field(
        None, title="报告id", description="只传report_id，则代表是对整个测试报告的所有步骤进行操作")
    report_case_id: Optional[int] = Field(default=None, title="报告用例id")
    report_step_id: Optional[int] = Field(default=None, title="报告步骤id")
    status: str = Field(ReportStepStatusEnum.RESUME, title="状态", description="stop、pause、resume")


class NotifyReportForm(GetReportForm):
    """ 通知报告 """
    notify_to: str = Field('default', title="发送渠道", description="default、ding_ding、we_chat、email")


class GetReportRerunCaseForm(GetReportForm):
    """ 获取报告 """
    result: str = Field('failed', title="执行结果", description="用例的执行结果，用于重跑，failed、pass")
