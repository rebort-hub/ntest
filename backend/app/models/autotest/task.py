# -*- coding: utf-8 -*-
import httpx

from ..base_model import BaseModel, fields, pydantic_model_creator
from app.schemas.enums import SendReportTypeEnum, ReceiveTypeEnum, DataStatusEnum
from config import job_server_host


class BaseTask(BaseModel):
    """ 定时任务基类表 """

    name = fields.CharField(255, default="", description="任务名称")
    num = fields.IntField(null=True, default=0, description="任务序号")

    env_list = fields.JSONField(default=[], description="运行环境")
    case_ids = fields.JSONField(default=[], description="用例id")
    task_type = fields.CharField(16, default="cron", description="定时类型")
    cron = fields.CharField(128, description="cron表达式")
    is_send = fields.CharEnumField(
        SendReportTypeEnum, default=SendReportTypeEnum.NOT_SEND, description="是否发送报告，not_send/always/on_fail")
    merge_notify = fields.IntField(
        default=0, null=True, description="多个环境时，是否合并通知（只通知一次），默认不合并，0不合并、1合并")
    receive_type = fields.CharEnumField(
        ReceiveTypeEnum, default=ReceiveTypeEnum.DING_DING, description="接收测试报告类型: ding_ding、we_chat、email")
    webhook_list = fields.JSONField(default=[], description="机器人地址")
    email_server = fields.CharField(255, null=True, description="发件邮箱服务器")
    email_from = fields.IntField(null=True, description="发件人邮箱")
    email_to = fields.JSONField(default=[], description="收件人邮箱")
    skip_holiday = fields.IntField(default=1, description="是否跳过节假日、调休日")
    status = fields.CharEnumField(
        DataStatusEnum, default=DataStatusEnum.DISABLE, description="任务的启用状态, enable/disable，默认disable")
    is_async = fields.IntField(default=0, description="任务的运行机制，0：串行，1：并行，默认0")
    suite_ids = fields.JSONField(default=[], description="用例集id")
    call_back = fields.JSONField(default=[], description="回调给流水线")
    project_id = fields.IntField(index=True, description="所属的服务id")
    push_hit = fields.IntField(default=1, null=True, description="任务不通过时，是否自动记录，0：不记录，1：记录，默认1")
    conf = fields.JSONField(
        default={"browser": "chrome", "server_id": "", "phone_id": "", "no_reset": ""},
        description="运行配置，ui存浏览器，app存运行服务器、手机、是否重置APP")

    class Meta:
        abstract = True  # 不生成表

    async def enable_task(self, task_type, user_id, token):
        """ 启用任务 """
        dict_task = dict(self)
        if "create_time" in dict_task: dict_task.pop("create_time")
        if "update_time" in dict_task: dict_task.pop("update_time")
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(
                    url=job_server_host,
                    headers={"access-token": token},
                    json={"user_id": user_id, "task": dict_task, "task_type": task_type}
                )
                await self.enable()
                return response.json()
        except Exception as error:
            raise ValueError("启用任务失败")

    async def disable_task(self, task_type, token):
        """ 禁用任务 """
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.request(
                    method="DELETE",
                    url=job_server_host,
                    headers={"access-token": token},
                    json={"task_code": f'{task_type}_{self.id}'}
                )
                await self.disable()
                return response.json()
        except Exception as error:
            raise ValueError("禁用任务失败")

    @classmethod
    async def clear_case_quote(cls, case_model, suite_model):
        """ 清理任务对于已删除的用例的引用 """
        task_list = await cls.all()
        for task in task_list:
            query_list = await case_model.filter(id__in=task.case_ids).all().values("id")
            case_id_list = [case_id["id"] for case_id in query_list]

            query_list = await suite_model.filter(id__in=task.suite_ids).all().values("id")
            suite_id_list = [suite_id["id"] for suite_id in query_list]

            await task.model_update({"case_ids": case_id_list, "suite_ids": suite_id_list})


class ApiTask(BaseTask):
    """ 定时任务表 """

    class Meta:
        table = "api_test_task"
        table_description = "接口测试任务表"


class AppTask(BaseTask):
    """ 测试任务表 """

    class Meta:
        table = "app_ui_test_task"
        table_description = "APP测试任务表"


class UiTask(BaseTask):
    """ 测试任务表 """

    class Meta:
        table = "web_ui_test_task"
        table_description = "web-ui测试任务表"


UiTaskPydantic = pydantic_model_creator(UiTask, name="UiTask")
AppTaskPydantic = pydantic_model_creator(AppTask, name="AppTask")
ApiTaskPydantic = pydantic_model_creator(ApiTask, name="ApiTask")
