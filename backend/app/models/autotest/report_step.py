# -*- coding: utf-8 -*-
import time

from ..base_model import BaseModel, fields, pydantic_model_creator
from ...schemas.enums import ReportStepStatusEnum


class BaseReportStep(BaseModel):
    """ 步骤执行记录基类表 """

    name = fields.CharField(128, description="测试步骤名称")
    case_id = fields.IntField(index=True, null=True, description="步骤所在的用例id")  # 如果是运行的接口，没有用例id
    step_id = fields.IntField(index=True, null=True, description="步骤id")  # 如果是运行的接口，没有步骤id
    element_id = fields.IntField(description="步骤对应的元素/接口id")
    report_case_id = fields.IntField(index=True, description="用例数据id")
    report_id = fields.IntField(index=True, description="测试报告id")
    status = fields.CharEnumField(
        ReportStepStatusEnum, default=ReportStepStatusEnum.RESUME, description="resume:放行、pause:暂停、stop:中断")
    process = fields.CharField(
        16, default='waite',
        description="步骤执行进度，waite：等待解析、parse: 解析数据、before：前置条件、after：后置条件、run：执行测试、extract：数据提取、validate：断言")
    result = fields.CharField(
        16, default='waite',
        description="步骤测试结果，waite：等待执行、running：执行中、fail：执行不通过、success：执行通过、skip：跳过、error：报错")
    step_data = fields.JSONField(default={}, description="步骤的数据")
    summary = fields.JSONField(
        default={},
        description="步骤的统计")

    class Meta:
        abstract = True  # 不生成表

    @staticmethod
    def get_summary_template():
        return {
            "start_at": "",
            "end_at": "",
            "step_duration": 0,  # 当前步骤执行耗时，只统计请求耗时
            "all_duration": 0  # 当前步骤开始执行 - 执行结束 整个过程的耗时，包含测试过程中的数据解析、等待...
        }

    @classmethod
    async def get_element_id_by_report_step_id(cls, report_step_id: list):
        """ 获取报告步骤对应的接口/元素id """
        if report_step_id:
            query_set = await cls.filter(id__in=report_step_id).values('element_id')
            return list(set([data["element_id"] for data in query_set]))
        return []

    @classmethod
    async def get_test_step_by_report_case(cls, report_case_id):
        """ 执行测试时，根据report_case_id 获取测试步骤 """
        report_step = await cls.filter(report_case_id=report_case_id).values("id", "step_data")
        report_step_list = []
        for data in report_step:
            data["step_data"]["report_step_id"] = data["id"]
            report_step_list.append(data["step_data"])
        return report_step_list

    @classmethod
    async def get_resport_step_list(cls, report_case_id, get_detail):
        """ 获取步骤列表，性能考虑，只查关键字段 """
        query_fields = ["id", "case_id", "name", "process", "result", "status"]
        if get_detail is True:
            query_fields.append("summary")
        return await cls.filter(report_case_id=report_case_id).values(*query_fields)

    @classmethod
    async def get_resport_step_list_by_report(cls, report_id):
        """ 获取步骤列表，性能考虑，只查关键字段 """
        query_fields = ["id", "case_id", "report_case_id", "name", "process", "result", "summary", "status"]
        return await cls.filter(report_id=report_id).values(*query_fields)

    @classmethod
    async def update_status(cls, report_id=None, report_case_id=None, report_step_id=None, status=ReportStepStatusEnum.RESUME):
        """ 修改步骤的执行状态, stop、pause、resume """
        if report_id and report_case_id is None and report_step_id is None:  # 更新整个测试报告的数据
            await cls.filter(report_id=report_id).update(status=status)
        elif report_id is None and report_case_id and report_step_id is None:  # 更新整个用例测试报告的数据
            await cls.filter(report_case_id=report_case_id).update(status=status)
        elif report_id is None and report_case_id and report_step_id:  # 更新用例下指定步骤及之后的测试报告的数据
            await cls.filter(report_case_id=report_case_id, id__gte=report_step_id).update(status=status)
        elif report_id is None and report_case_id is None and report_step_id:  # 更新指定数据的状态
            await cls.filter(id=report_step_id).update(status=status)

    @classmethod
    async def get_resport_step_with_status(cls, resport_step_id, time_out=60):
        """ 如果步骤的状态是暂停，则等暂停完毕或者暂停超时结束后再返回，模拟debug """
        while time_out >= 0:
            report_step = await cls.filter(id=resport_step_id).first()
            if report_step.status == "pause":  # 如果设置了当前步骤为暂停执行，则每5秒查询一次状态有没有变更
                time_out -= 5
                time.sleep(5)
                if time_out >= 5:  # 最后一次循环就不重置 report_step 变量了
                    report_step = None
                continue
            return report_step

        # 步骤暂停超时过后还没有放行，把后面的所有步骤都改为停止执行
        await cls.update_status(None, report_step.report_case_id, report_step.id, "stop")
        report_step.status = "stop"
        return report_step

    async def save_step_result_and_summary(self, step_runner, step_error_traceback=None):
        """ 保存测试步骤的结果和数据 """
        data = step_runner.get_test_step_data()
        step_data = self.loads(self.dumps(data))  # 可能有 datetime 格式的数据
        step_meta_data = step_runner.client_session.meta_data
        step_data["attachment"] = step_error_traceback
        # 保存测试步骤的结果和数据
        await self.update_report_step_data(
            step_data=step_data, result=step_meta_data["result"], summary=step_meta_data["stat"])

    @classmethod
    def add_run_step_result_count(cls, case_summary, step_meta_data, response_time_level=None, report_step_id=None):
        """ 记录步骤执行结果数量 """
        # 结果测试维度
        if step_meta_data["result"] == "success":
            case_summary["stat"]["success"] += 1
            case_summary["time"]["step_duration"] += step_meta_data["stat"]["elapsed_ms"]
        elif step_meta_data["result"] == "fail":
            case_summary["stat"]["fail"] += 1
            case_summary["time"]["step_duration"] += step_meta_data["stat"]["elapsed_ms"]
        elif step_meta_data["result"] == "error":
            case_summary["stat"]["error"] += 1
        elif step_meta_data["result"] == "skip":
            case_summary["stat"]["skip"] += 1

        # 接口响应耗时维度
        if response_time_level is not None:
            if step_meta_data["stat"]["elapsed_ms"] > response_time_level.get("very_slow", 1000):
                case_summary["stat"]["response_time"]["very_slow"].append(report_step_id)
            elif step_meta_data["stat"]["elapsed_ms"] > response_time_level.get("slow", 300):
                case_summary["stat"]["response_time"]["slow"].append(report_step_id)

    async def update_report_step_data(self, **kwargs):
        """ 更新测试数据 """
        await self.__class__.filter(id=self.id).update(**kwargs)

    async def update_test_result(self, result, step_data):
        """ 更新测试状态 """
        update_dict = {"result": result}
        if step_data:
            if isinstance(step_data, dict):
                step_data = self.dumps(step_data)
            update_dict["step_data"] = step_data
        await self.__class__.filter(id=self.id).update(**update_dict)

    async def test_is_running(self, step_data=None):
        if isinstance(step_data, dict):
            step_data = self.dumps(step_data)
        await self.update_test_result("running", step_data)

    async def test_is_fail(self, step_data=None):
        if isinstance(step_data, dict):
            step_data = self.dumps(step_data)
        await self.update_test_result("fail", step_data)

    async def test_is_success(self, step_data=None):
        if isinstance(step_data, dict):
            step_data = self.dumps(step_data)
        await self.update_test_result("success", step_data)

    async def test_is_skip(self, step_data=None):
        if isinstance(step_data, dict):
            step_data = self.dumps(step_data)
        await self.update_test_result("skip", step_data)

    async def test_is_error(self, step_data=None):
        if isinstance(step_data, dict):
            step_data = self.dumps(step_data)
        await self.update_test_result("error", step_data)

    async def update_step_process(self, process, step_data):
        """ 更新数据和执行进度 """
        update_dict = {"process": process}
        if step_data:
            if isinstance(step_data, dict):
                step_data = self.dumps(step_data)
            update_dict["step_data"] = step_data

        await self.__class__.filter(id=self.id).update(**update_dict)

    async def test_is_start_parse(self, step_data=None):
        if isinstance(step_data, dict):
            step_data = self.dumps(step_data)
        await self.update_step_process("parse", step_data)

    async def test_is_start_before(self, step_data=None):
        if isinstance(step_data, dict):
            step_data = self.dumps(step_data)
        await self.update_step_process("before", step_data)

    async def test_is_start_running(self, step_data=None):
        if isinstance(step_data, dict):
            step_data = self.dumps(step_data)
        await self.update_step_process("run", step_data)

    async def test_is_start_extract(self, step_data=None):
        if isinstance(step_data, dict):
            step_data = self.dumps(step_data)
        await self.update_step_process("extract", step_data)

    async def test_is_start_after(self, step_data=None):
        if isinstance(step_data, dict):
            step_data = self.dumps(step_data)
        await self.update_step_process("after", step_data)

    async def test_is_start_validate(self, step_data=None):
        if isinstance(step_data, dict):
            step_data = self.dumps(step_data)
        await self.update_step_process("validate", step_data)


class ApiReportStep(BaseReportStep):
    class Meta:
        table = "api_test_report_step"
        table_description = "接口测试报告的步骤数据表"


class UiReportStep(BaseReportStep):
    element_id = fields.IntField(description="步骤对应的元素id")

    class Meta:
        table = "web_ui_test_report_step"
        table_description = "web-ui测试报告的步骤数据表"


class AppReportStep(BaseReportStep):
    element_id = fields.IntField(description="步骤对应的元素id")

    class Meta:
        table = "app_ui_test_report_step"
        table_description = "APP测试报告的步骤数据表"


ApiReportStepPydantic = pydantic_model_creator(ApiReportStep, name="ApiReportStep")
AppReportStepPydantic = pydantic_model_creator(AppReportStep, name="AppReportStep")
UiReportStepPydantic = pydantic_model_creator(UiReportStep, name="UiReportStep")
