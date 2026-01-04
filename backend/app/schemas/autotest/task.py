from typing import Optional, Union, List
from pydantic import Field
from crontab import CronTab

from ..base_form import BaseForm, PaginationForm, ChangeSortForm
from app.schemas.enums import ReceiveTypeEnum, SendReportTypeEnum, TriggerTypeEnum


class GetTaskListForm(PaginationForm):
    """ 获取任务列表 """
    project_id: int = Field(..., title="服务id")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        return {"project_id": self.project_id}


class GetTaskForm(BaseForm):
    """ 校验任务id已存在 """
    id: int = Field(..., title="任务id")



class AddTaskForm(BaseForm):
    """ 添加定时任务的校验 """
    project_id: int = Field(..., title="服务id")
    suite_ids: Optional[list] = Field(default=None, title="用例集id")
    case_ids: Optional[list] = Field(default=None, title="用例id")
    env_list: list = Field(..., title="运行环境")
    name: str = Field(..., title="任务名")
    is_send: SendReportTypeEnum = Field(
        SendReportTypeEnum.ON_FAIL, title="是否发送测试报告", description="not_send/always/on_fail")
    receive_type: ReceiveTypeEnum = Field(
        ReceiveTypeEnum.DING_DING, title="接收测试报告类型", description="ding_ding、we_chat、email")
    webhook_list: list = Field(title="接收消息机器人地址")
    email_server: Optional[str] = Field(default=None, title="发件邮箱服务器")
    email_to: List[int] = Field(title="收件人邮箱")
    email_from: Optional[int] = Field(default=None, title="发件人邮箱")
    merge_notify: Optional[int] = Field(
        0, title="多个环境时，是否合并通知（只通知一次）", description="默认不合并，0不合并、1合并")
    cron: str = Field(..., title="cron表达式")
    skip_holiday: int = Field(default=1, title="是否跳过节假日、调休日")
    conf: Optional[dict] = Field({}, title="运行配置", description="ui存浏览器，app存运行服务器、手机、是否重置APP")
    is_async: int = Field(default=0, title="任务的运行机制", description="0：串行，1：并行，默认0")
    call_back: Optional[Union[list, dict]] = Field(title="回调给流水线")
    push_hit: int = Field(title="任务不通过时，是否自动记录问题", description="任务不通过时，是否自动记录，0：不记录，1：记录，默认1")

    def validate_is_send(self):
        """ 发送报告类型 """
        if self.is_send in [SendReportTypeEnum.ALWAYS, SendReportTypeEnum.ON_FAIL]:
            if self.receive_type in (ReceiveTypeEnum.DING_DING, ReceiveTypeEnum.WE_CHAT):
                self.validate_is_true('选择了要通过机器人发送报告，则webhook地址必填', self.webhook_list)
            elif self.receive_type == ReceiveTypeEnum.EMAIL:
                self.validate_email(self.email_server, self.email_from, self.email_to)

    def validate_cron(self):
        """ 校验cron格式 """
        try:
            if len(self.cron.strip().split(" ")) == 6:
                CronTab(self.cron + " *")
        except Exception as error:
            raise ValueError(f"时间配置【{self.cron}】错误，需为cron格式, 请检查")
        if self.cron.startswith("*"):  # 每秒钟
            raise ValueError(f"设置的执行频率过高，请重新设置")

    def validate_attrib(self):
        self.validate_is_true(self.name, "任务名不可为空")
        self.validate_is_true(self.env_list, "运行环境不可为空")

    async def validate_request(self, *args, **kwargs):
        self.validate_attrib()
        self.validate_is_send()
        self.validate_cron()


class EditTaskForm(AddTaskForm, GetTaskForm):
    """ 编辑任务 """

    async def validate_request(self, *args, **kwargs):
        self.validate_attrib()
        self.validate_is_send()
        self.validate_cron()


class RunTaskForm(BaseForm):
    """ 运行任务 """
    id_list: list = Field(..., title="任务id list")
    env_list: Optional[list] = Field(default=None, title="运行环境")
    is_async: int = Field(default=0, title="任务的运行机制", description="0：串行，1：并行，默认0")
    trigger_type: Optional[TriggerTypeEnum] = Field(
        TriggerTypeEnum.PAGE, title="触发类型", description="pipeline/page/cron")  # pipeline 跑完过后会发送测试报告
    extend: Optional[Union[list, dict, str]] = Field(title="运维传过来的扩展字段，接收的什么就返回什么")

    browser: Optional[str] = Field(default="chrome", title="运行浏览器（ui自动化必传）")
    server_id: Optional[int] = Field(default=None, title="执行服务器（app自动化必传）")
    phone_id: Optional[int] = Field(default=None, title="执行手机（app自动化必传）")
    no_reset: Optional[bool] = Field(default=False, title="是否不重置手机（app自动化必传）")
