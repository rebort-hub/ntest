# -*- coding: utf-8 -*-
import datetime
import time

from ..base_model import BaseModel, fields, pydantic_model_creator
from app.schemas.enums import TriggerTypeEnum


class BaseReport(BaseModel):
    """ 测试报告基类表 """

    name = fields.CharField(128, description="测试报告名称")
    is_passed = fields.IntField(default=1, description="是否全部通过，1全部通过，0有报错")
    # is_async = fields.IntField(default=0, description="任务的运行机制，0：用例维度串行执行，1：用例维度并行执行")
    run_type = fields.CharField(16, default="task", description="报告类型，task/suite/case/api")
    status = fields.IntField(default=1, description="当前节点是否执行完毕，1执行中，2执行完毕")
    retry_count = fields.IntField(default=0, description="已经执行重试的次数")
    env = fields.CharField(128, default="test", description="运行环境")
    temp_variables = fields.JSONField(null=True, default={}, description="临时参数")
    process = fields.IntField(default=1, description="进度节点, 1: 解析数据、2: 执行测试、3: 写入报告")
    trigger_type = fields.CharEnumField(
        TriggerTypeEnum, default=TriggerTypeEnum.PAGE, description="触发类型，pipeline:流水线、page:页面、cron:定时任务")
    batch_id = fields.CharField(128, index=True, description="运行批次id，用于查询报告")
    # run_id = fields.JSONField(description="运行id，用于触发重跑接口/用例/用例集/任务")
    trigger_id = fields.JSONField(null=True, comment="运行id，用于触发重跑")
    project_id = fields.IntField(index=True, description="所属的服务id")
    summary = fields.JSONField(default={}, description="报告的统计")
    notified = fields.BooleanField(default=False, description="标记是否已经通知过了")

    class Meta:
        abstract = True  # 不生成表

    @staticmethod
    def get_summary_template():
        return {
            "result": "success",
            "stat": {
                "test_case": {  # 用例维度
                    "total": 0,
                    "success": 0,
                    "fail": 0,
                    "error": 0,
                    "skip": 0
                },
                "test_step": {  # 步骤维度
                    "total": 0,
                    "success": 0,
                    "fail": 0,
                    "error": 0,
                    "skip": 0
                },
                "count": {  # 此次运行有多少接口/元素
                    "api": 1,
                    "step": 1,
                    "element": 0
                },
                "response_time": {  # 记录步骤响应速度统计
                    "slow": [],
                    "very_slow": []
                }
            },
            "time": {  # 时间维度
                "start_at": "",
                "end_at": "",
                "step_duration": 0,  # 所有步骤的执行耗时，只统计请求耗时
                "case_duration": 0,  # 所有用例下所有步骤执行耗时，只统计请求耗时
                "all_duration": 0  # 开始执行 - 执行结束 整个过程的耗时，包含测试过程中的数据解析、等待...
            },
            "env": {  # 环境
                "code": "",
                "name": "",
            }
        }

    @classmethod
    def get_batch_id(cls, user_id):
        """ 生成运行批次id """
        return f'{user_id}_{int(time.time() * 1000000)}'

    @classmethod
    async def get_new_report(cls, **kwargs):
        """ 生成一个测试报告 """
        if "summary" not in kwargs:
            kwargs["summary"] = cls.get_summary_template()
        return await cls.create(**kwargs)

    def merge_test_result(self, case_summary):
        """ 汇总测试数据和结果
        Args:
            case_summary_list (list): list of (testcase, result)
        """
        self.summary["stat"]["test_case"]["total"] += 1
        self.summary["stat"]["test_case"][case_summary["result"]] += 1
        self.summary["stat"]["test_step"]["total"] += case_summary["stat"]["total"]
        self.summary["stat"]["test_step"]["fail"] += case_summary["stat"]["fail"]
        self.summary["stat"]["test_step"]["error"] += case_summary["stat"]["error"]
        self.summary["stat"]["test_step"]["skip"] += case_summary["stat"]["skip"]
        self.summary["stat"]["test_step"]["success"] += case_summary["stat"]["success"]
        self.summary["stat"]["response_time"]["slow"] = list(
            set(self.summary["stat"]["response_time"]["slow"] + case_summary["stat"]["response_time"]["slow"]))
        self.summary["stat"]["response_time"]["very_slow"] = list(set(
            self.summary["stat"]["response_time"]["very_slow"] + case_summary["stat"]["response_time"]["very_slow"]))
        self.summary["time"]["step_duration"] += case_summary["time"]["step_duration"]
        self.summary["time"]["case_duration"] += case_summary["time"]["case_duration"]
        if self.summary["result"] != "fail":
            match case_summary["result"]:
                case "success":
                    self.summary["result"] = "success"
                case _:
                    self.summary["result"] = "fail"

        return self.summary

    @classmethod
    async def get_last_10_minute_running_count(cls):
        """ 获取最近10分钟产生的，状态为运行中的报告数量，用于判断是否需要把运行任务放到队列中 """
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_10_minute = (datetime.datetime.now() + datetime.timedelta(minutes=-10)).strftime("%Y-%m-%d %H:%M:%S")
        return await cls.filter(process__not=3, status__not=2, create_time__range=[last_10_minute, now]).count()

    async def update_report_process(self, **kwargs):
        """ 开始解析数据 """
        await self.__class__.filter(id=self.id).update(**kwargs)

    async def parse_data_start(self):
        """ 开始解析数据 """
        await self.update_report_process(process=1, status=1)

    async def parse_data_finish(self):
        """ 数据解析完毕 """
        await self.update_report_process(process=1, status=2)

    async def run_case_start(self):
        """ 开始运行测试 """
        await self.update_report_process(process=2, status=1)

    async def run_case_finish(self):
        """ 测试运行完毕 """
        await self.update_report_process(process=2, status=2)

    async def save_report_start(self):
        """ 开始保存报告 """
        await self.update_report_process(process=3, status=1)

    async def save_report_finish(self):
        """ 保存报告完毕 """
        await self.update_report_process(process=3, status=2)

    @classmethod
    async def batch_delete_report(cls, report_list):
        """ 批量删除报告 """
        await cls.filter(id__in=report_list).delete()

    @classmethod
    async def batch_delete_report_detail_data(cls, report_case_mode, report_step_mode):
        """ 批量删除已删除报告下的用例报告、步骤报告 """
        all_report_list = [report["id"] for report in await cls.all().values("id")]
        await report_case_mode.filter(report_id__not_in=all_report_list).delete()
        await report_step_mode.filter(report_id__not_in=all_report_list).delete()

    async def update_report_result(self, run_result, status=2, summary=None):
        """ 测试运行结束后，更新状态和结果 """
        update_dict = {"is_passed": 1 if run_result == "success" else 0, "status": status}
        if summary:
            update_dict["summary"] = summary
            self.summary = summary
        self.is_passed = update_dict["is_passed"]
        await self.__class__.filter(id=self.id).update(**update_dict)

    @classmethod
    async def select_is_all_status_by_batch_id(cls, batch_id, process_and_status=[1, 1]):
        """ 查询一个运行批次下离初始化状态最近的报告 """
        status_list = [[1, 1], [1, 2], [2, 1], [2, 2], [3, 1], [3, 2]]
        index = status_list.index(process_and_status)
        for process, status in status_list[index:]:  # 只查传入状态之后的状态
            if await cls.filter(batch_id=batch_id, process=process, status=status).values("id"):
                return {"process": process, "status": status}

    @classmethod
    async def select_is_all_done_by_batch_id(cls, batch_id):
        """ 报告是否全部生成 """
        return await cls.filter(batch_id=batch_id, process__not=3, status__not=2).first() is None

    @classmethod
    async def select_show_report_id(cls, batch_id):
        """ 获取一个运行批次要展示的报告 """
        fail_report = await cls.filter(batch_id=batch_id, is_passed=0).first()
        if fail_report:
            return fail_report.id
        else:
            success_report = await cls.filter(batch_id=batch_id).first()
            return success_report.id


class ApiReport(BaseReport):
    class Meta:
        table = "api_test_report"
        table_description = "接口测试报告表"


class AppReport(BaseReport):
    class Meta:
        table = "app_ui_test_report"
        table_description = "APP测试报告表"


class UiReport(BaseReport):
    class Meta:
        table = "web_ui_test_report"
        table_description = "web-ui测试报告表"


ApiReportPydantic = pydantic_model_creator(ApiReport, name="ApiReport")
AppReportPydantic = pydantic_model_creator(AppReport, name="AppReport")
UiReportPydantic = pydantic_model_creator(UiReport, name="UiReport")
