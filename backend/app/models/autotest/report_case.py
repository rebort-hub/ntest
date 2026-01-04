# -*- coding: utf-8 -*-
import copy

from ..base_model import BaseModel, fields, pydantic_model_creator


class BaseReportCase(BaseModel):
    """ 用例执行记录基类表 """

    name = fields.CharField(128, description="测试用例名称")
    case_id = fields.IntField(null=True, index=True, default=0,
                              description="执行记录对应的用例id, 如果是运行接口，则为null")
    suite_id = fields.IntField(null=True, index=True, default=0, description="执行用例所在的用例集id")
    report_id = fields.IntField(index=True, description="测试报告id")
    result = fields.CharField(
        128, default='waite',
        description="步骤测试结果，waite：等待执行、running：执行中、fail：执行不通过、success：执行通过、skip：跳过、error：报错")
    case_data = fields.JSONField(default={}, description="用例的数据")
    summary = fields.JSONField(default={}, description="用例的报告统计")
    error_msg = fields.TextField(default='', description="用例错误信息")

    class Meta:
        abstract = True  # 不生成表

    @staticmethod
    def get_summary_template():
        return {
            "result": "skip",
            "stat": {
                'total': 1,  # 初始化的时候给个1，方便用户查看运行中的报告，后续会在流程中更新为实际的total
                'fail': 0,
                'error': 0,
                'skip': 0,
                'success': 0,
                "response_time": {  # 记录步骤响应速度统计
                    "slow": [],
                    "very_slow": []
                },
            },
            "time": {
                "start_at": "",
                "end_at": "",
                "step_duration": 0,  # 当前用例的步骤执行耗时，只统计请求耗时
                "case_duration": 0,  # 当前用例下所有步骤执行耗时，只统计请求耗时
                "all_duration": 0  # 用例开始执行 - 执行结束 整个过程的耗时，包含测试过程中的数据解析、等待...
            }
        }

    async def save_case_result_and_summary(self):
        """ 保存测试用例的结果和数据 """
        # 耗时
        self.summary["time"]["case_duration"] = round(self.summary["time"]["step_duration"] / 1000, 4)  # 毫秒转秒
        self.summary["time"]["all_duration"] = (
                self.summary["time"]["end_at"] - self.summary["time"]["start_at"]).total_seconds()
        self.summary["time"]["start_at"] = self.summary["time"]["start_at"].strftime("%Y-%m-%d %H:%M:%S.%f")
        self.summary["time"]["end_at"] = self.summary["time"]["end_at"].strftime("%Y-%m-%d %H:%M:%S.%f")

        # 状态
        if self.summary["stat"]["fail"] or self.summary["stat"]["error"]:  # 步骤里面有不通过或者错误，则把用例的结果置为不通过
            self.summary["result"] = "fail"
            await self.test_is_fail(summary=self.summary)
        else:
            self.summary["result"] = "success"
            await self.test_is_success(summary=self.summary)

    @classmethod
    async def get_resport_case_list(cls, report_id, suite_id=None, get_detail=False):
        """ 根据报告id，获取用例列表，性能考虑，只查关键字段 """
        query_fields = ["id", "case_id", "suite_id", "name", "result"]  # 执行进度展示
        if get_detail:
            query_fields.extend(["summary"])  # 报告展示
            # query_fields.extend(["summary", "case_data", "error_msg"])  # 报告展示

        filter_dict = {"report_id": report_id, "suite_id": suite_id} if suite_id else {"report_id": report_id}
        return await cls.filter(**filter_dict).values(*query_fields)  # 报告展示，根据用例集id查

    @classmethod
    async def get_resport_suite_list(cls, report_id, case_suite_model):
        """ 根据报告id，获取用例集列表 """
        # 一次性查询所有数据，使用 JOIN 来减少查询次数
        query_res = await cls.raw(f"""
                  SELECT r.result,
                         r.suite_id,
                         s.name
                  FROM {cls._meta.db_table} r
                        JOIN {case_suite_model._meta.db_table} s 
                        ON r.suite_id = s.id
                  WHERE r.report_id = {report_id}
                  ORDER BY s.num ASC
            """)

        # 把数据解析成固定格式
        # [{'id': 2, 'name': '单接口用例集', 'result': ['fail', 'success']}, {'id': 3, 'name': '流程用例集', 'result': ['fail']}]
        suite_dict = {}
        for report_case in query_res:
            if report_case.suite_id not in suite_dict:
                suite_dict[report_case.suite_id] = {
                    "id": report_case.suite_id,
                    "name": report_case.name,
                    "result": [report_case.result],
                    "children": []
                }
                continue
            suite_dict[report_case.suite_id]["result"].append(report_case.result)

        def parse_suite_result(suite_item):
            """ 判断用例集状态，并加入到最终结果 """
            if "error" in suite_item["result"]:
                suite_item["result"] = "error"
            elif "fail" in suite_item["result"]:
                suite_item["result"] = "fail"
            elif "success" in suite_item["result"]:
                suite_item["result"] = "success"
            elif "skip" in suite_item["result"]:
                suite_item["result"] = "skip"
            elif "running" in suite_item["result"]:
                suite_item["result"] = "running"
            elif "wait" in suite_item["result"]:
                suite_item["result"] = "wait"
            return suite_item

        return [parse_suite_result(suite_item) for suite_item in suite_dict.values()]

    @classmethod
    async def get_resport_suite_and_case_list(cls, report_id, suite_model, report_step_model):
        """ 根据报告id，获取用例集/用例列表 """
        # 报告可能是用例，可能是接口
        suite_list = await cls.get_resport_suite_list(report_id, suite_model)
        resport_case_list = await cls.get_resport_case_list(report_id, get_detail=True)
        if not resport_case_list:  # 报告可能已经被清除了
            return []
        if not suite_list:  # 跑的是接口，没有用例集归属，需要手动生成
            suite_list = [{
                "id": resport_case_list[0]["suite_id"],
                "name": resport_case_list[0]["name"],
                "result": resport_case_list[0]["result"],
                "children": []
            }]
        resport_step_list = await report_step_model.get_resport_step_list_by_report(report_id)
        for suite_item in suite_list:
            for resport_case_index, resport_case_item in enumerate(resport_case_list):
                if resport_case_item["suite_id"] == suite_item["id"]:
                    resport_case_item["children"] = []
                    for resport_step_index, resport_step_item in enumerate(resport_step_list):
                        if resport_step_item["report_case_id"] == resport_case_item["id"]:
                            resport_case_item["children"].append(resport_step_item)
                    suite_item["children"].append(resport_case_item)
        return suite_list

    async def update_report_case_data(self, case_data, summary=None):
        """ 更新测试数据 """
        update_dict = {"case_data": case_data}
        if summary:
            update_dict["summary"] = summary
        await self.__class__.filter(id=self.id).update(**update_dict)

    async def update_report_case_result(self, result, case_data, summary, error_msg):
        """ 更新测试状态 """
        update_dict = {"result": result}
        if case_data:
            update_dict["case_data"] = case_data
        if summary:
            update_dict["summary"] = summary
        if error_msg:
            update_dict["error_msg"] = error_msg
        await self.__class__.filter(id=self.id).update(**update_dict)

    async def test_is_running(self, case_data=None, summary=None):
        await self.update_report_case_result("running", case_data, summary, error_msg=None)

    async def test_is_fail(self, case_data=None, summary=None):
        await self.update_report_case_result("fail", case_data, summary, error_msg=None)

    async def test_is_success(self, case_data=None, summary=None):
        await self.update_report_case_result("success", case_data, summary, error_msg=None)

    async def test_is_skip(self, case_data=None, summary=None):
        await self.update_report_case_result("skip", case_data, summary, error_msg=None)

    async def test_is_error(self, case_data=None, summary=None, error_msg=None):
        await self.update_report_case_result("error", case_data, summary, error_msg)


class ApiReportCase(BaseReportCase):
    class Meta:
        table = "api_test_report_case"
        table_description = "测试报告用例表"


class AppReportCase(BaseReportCase):
    class Meta:
        table = "app_ui_test_report_case"
        table_description = "APP测试报告的用例数据表"


class UiReportCase(BaseReportCase):
    class Meta:
        table = "web_ui_test_report_case"
        table_description = "web-ui测试报告的用例数据表"


UiReportCasePydantic = pydantic_model_creator(UiReportCase, name="UiReportCase")
AppReportCasePydantic = pydantic_model_creator(AppReportCase, name="AppReportCase")
ApiReportCasePydantic = pydantic_model_creator(ApiReportCase, name="ApiReportCase")
