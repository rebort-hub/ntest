import copy
import types
import importlib

from app.models.autotest.model_factory import ApiProject, ApiProjectEnv, ApiCaseSuite, ApiCase, ApiStep, ApiMsg, \
    ApiReport, ApiReportCase, ApiReportStep, UiProject, UiProjectEnv, UiElement, UiCaseSuite, UiCase, UiStep, UiReport, \
    UiReportCase, UiReportStep, AppProject, AppProjectEnv, AppElement, AppCaseSuite, AppCase, AppStep, AppReport, \
    AppReportCase, AppReportStep
from app.models.assist.hits import Hits
from app.models.config.webhook import WebHook
from app.schemas.enums import TriggerTypeEnum, ReceiveTypeEnum, ReportStepStatusEnum
from app.models.system.user import User
from app.models.config.model_factory import RunEnv
from app.models.assist.model_factory import Script
from app.models.config.model_factory import Config
from utils.client.test_runner.api import TestRunner
from utils.client.test_runner.utils import build_url
from utils.client.parse_model import ProjectModel, ApiModel, CaseModel, ElementModel
from utils.message.send_report import send_report, call_back_for_pipeline
from utils.client.test_runner import validate_func
from utils.logs.log import logger

class RunTestRunner:

    def __init__(
            self, report_id=None, env_code=None, env_name=None, run_type="api", extend={}, task_dict={}, insert_to=None
    ):
        self.env_code = env_code  # 运行环境id
        self.env_name = env_name  # 运行环境名，用于发送即时通讯
        self.extend = extend
        self.report_id = report_id
        self.run_type = run_type
        self.task_dict = task_dict
        self.insert_to = insert_to  # 把当前产生的报告的用例和步骤执行记录插入到指定的报告下（重跑并插入）

        self.time_out = 60
        self.wait_time_out = 5
        self.count_step = 0
        self.api_set = set()
        self.element_set = set()
        self.parsed_project_dict = {}
        self.parsed_case_dict = {}
        self.parsed_api_dict = {}
        self.parsed_element_dict = {}
        self.run_env = None
        self.report = None
        self.api_model = ApiMsg
        self.element_model = None

        match self.run_type:
            case "api":  # 接口自动化
                self.project_model = ApiProject
                self.project_env_model = ApiProjectEnv
                self.suite_model = ApiCaseSuite
                self.case_model = ApiCase
                self.step_model = ApiStep
                self.report_model = ApiReport
                self.report_case_model = ApiReportCase
                self.report_step_model = ApiReportStep
            case "ui":  # web-ui自动化
                self.project_model = UiProject
                self.project_env_model = UiProjectEnv
                self.element_model = UiElement
                self.suite_model = UiCaseSuite
                self.case_model = UiCase
                self.step_model = UiStep
                self.report_model = UiReport
                self.report_case_model = UiReportCase
                self.report_step_model = UiReportStep
            case _:  # app-ui自动化
                self.project_model = AppProject
                self.project_env_model = AppProjectEnv
                self.element_model = AppElement
                self.suite_model = AppCaseSuite
                self.case_model = AppCase
                self.step_model = AppStep
                self.report_model = AppReport
                self.report_case_model = AppReportCase
                self.report_step_model = AppReportStep

        # testRunner需要的数据格式
        self.test_plan = {
            "is_async": 0,
            "run_type": self.run_type,
            "report_id": self.report_id,
            "report_model": self.report_model,
            "report_case_model": self.report_case_model,
            "report_step_model": self.report_step_model,
            "response_time_level": {"slow": 0, "very_slow": 0},
            "project_mapping": {
                "functions": {},
                "variables": {},
            },
            "report_case_list": [],  # 用例
        }

        self.init_parsed_data()

    def init_parsed_data(self):
        self.parsed_project_dict = {}
        self.parsed_case_dict = {}
        self.parsed_api_dict = {}
        self.parsed_element_dict = {}
        self.run_env = None

    # async def get_report_addr(self):
    #     """ 获取报告前端地址 """
    #     report_host = await Config.get_report_host()
    #     if self.run_type == "api":  # 接口自动化
    #         report_addr = await Config.get_api_report_addr()
    #         return f'{report_host}{report_addr}'
    #     elif self.run_type == "ui":  # web-ui自动化
    #         report_addr = await Config.get_web_ui_report_addr()
    #         return f'{report_host}{report_addr}'
    #     else:  # app-ui自动化
    #         report_addr = await Config.get_app_ui_report_addr()
    #         return f'{report_host}{report_addr}'

    async def get_format_project(self, project_id):
        """ 从已解析的服务字典中取指定id的服务，如果没有，则取出来解析后放进去 """
        if not self.run_env:
            self.run_env = await RunEnv.filter(code=self.env_code).first()

        if project_id not in self.parsed_project_dict:
            project = await self.project_model.filter(id=project_id).first()
            await self.parse_functions(project.script_list)

            project_env = await self.project_env_model.filter(env_id=self.run_env.id, project_id=project.id).first()

            data = dict(project_env) | dict(project) | dict(self.run_env)
            self.parsed_project_dict.update({project_id: ProjectModel(**data)})
        return self.parsed_project_dict[project_id]

    async def get_format_case(self, case_id):
        """ 从已解析的用例字典中取指定id的用例，如果没有，则取出来解析后放进去 """
        if case_id not in self.parsed_case_dict:
            case = await self.case_model.filter(id=case_id).first()
            if not case:
                return  # 可能存在任务选择了用例，在那边直接把这条用例删掉了的情况
            self.parsed_case_dict.update({case_id: CaseModel(**dict(case))})
        return self.parsed_case_dict[case_id]

    async def get_format_element(self, element_id):
        """ 从已解析的元素字典中取指定id的元素，如果没有，则取出来解析后放进去 """
        if element_id not in self.parsed_element_dict:
            element = await self.element_model.filter(id=element_id).first()
            self.parsed_element_dict.update({element_id: ElementModel(**dict(element))})
        return self.parsed_element_dict[element_id]

    async def get_format_api(self, project, api_id=None, api_obj=None):
        """ 从已解析的接口字典中取指定id的接口，如果没有，则取出来解析后放进去 """
        if api_obj:
            api_id = api_obj.id
        if api_id not in self.parsed_api_dict:
            api = api_obj or await ApiMsg.filter(id=api_id).first()
            if api.project_id not in self.parsed_project_dict:
                project = await self.project_model.filter(id=api.project_id).first()
                await self.parse_functions(project.script_list)
            self.parsed_api_dict.update({api.id: self.parse_api(project, ApiModel(**dict(api)))})
        return self.parsed_api_dict[api_id]

    async def parse_functions(self, func_file_id_list):
        """ 获取自定义函数 """
        for func_file_id in func_file_id_list:
            query_set = await Script.filter(id=func_file_id).values("name")
            func_file_data = importlib.reload(
                importlib.import_module(f'script_list.{self.env_code}_{query_set[0]["name"]}'))
            self.test_plan["project_mapping"]["functions"].update({
                name: item for name, item in vars(func_file_data).items() if isinstance(item, types.FunctionType)
            })

    def parse_case_is_skip(self, skip_if_list, server_id=None, phone_id=None):
        """ 判断是否跳过用例，暂时只支持对运行环境的判断 """
        for skip_if in skip_if_list:
            skip_type = skip_if["skip_type"]
            if skip_if["data_source"] == "run_env":
                skip_if["check_value"] = self.env_code
            elif skip_if["data_source"] == "run_server":
                skip_if["check_value"] = server_id
            elif skip_if["data_source"] == "run_device":
                skip_if["check_value"] = phone_id
            try:
                comparator = getattr(validate_func, skip_if["comparator"])  # 借用断言来判断条件是否为真
                skip_if_result = comparator(skip_if["check_value"], skip_if["expect"])  # 通过没有返回值
            except Exception as error:
                skip_if_result = error
            if (skip_type == "and" and skip_if_result is None) or (skip_type == "or" and skip_if_result is None):
                return True

    def parse_ui_test_step(self, project, element, step):
        """ 解析 UI自动化测试步骤
        project: 当前步骤对应元素所在的项目(解析后的)
        element: 解析后的element
        step: 原始step
        返回解析后的步骤 {}
        """
        return {
            "name": step.name,
            "setup_hooks": step.up_func,
            "teardown_hooks": step.down_func,
            # "skip": not step.status,  # 无条件跳过当前测试
            "skip_if": step.skip_if,  # 如果条件为真，则跳过当前测试
            # "skip_unless": "",  # 除非条件为真，否则跳过当前测试
            "times": step.run_times,  # 运行次数
            "extract": step.extracts,  # 要提取的信息
            "validate": step.validates,  # 断言信息
            "test_action": {
                "execute_name": step.execute_name,
                "action": step.execute_type,
                "by_type": element.by,
                # 如果是打开页面，则设置为项目域名+页面地址
                "element": build_url(project.host, element.element) if element.by == "url" else element.element,
                "text": step.send_keys,
                "wait_time_out": float(step.wait_time_out or element.wait_time_out or self.wait_time_out)
            }
        }

    async def save_report_and_send_message(self, result):
        """ 写入测试报告到数据库, 并把数据写入到文本中 """
        logger.info(f'开始保存测试报告')
        await self.report.save_report_start()
        await self.report.update_report_result(result["result"], summary=result)
        await self.report.save_report_finish()
        await self.push_hit_if_fail(result["result"])
        logger.info(f'测试报告保存完成')

        # 有可能是多环境一次性批量运行，根据batch_id查是否全部运行完毕
        if await self.report_model.select_is_all_done_by_batch_id(self.report.batch_id):
            if self.task_dict.get("merge_notify") != 1:  # 不合并通知
                # 有失败的，则获取失败的报告, 否则只发送当前测试结果的报告
                not_passed = await self.report_model.filter(batch_id=self.report.batch_id, is_passed=0).first().values(
                    "id", "summary")

                if not_passed:
                    report_id, report_summary = not_passed["id"], not_passed["summary"]
                else:
                    report_id, report_summary = self.report.id, result

                if self.run_type == "api":  # 接口自动化，为了报告的精准性，慢接口的统计精确到接口个数
                    report_summary["stat"]["response_time"][
                        "slow"] = await ApiReportStep.get_element_id_by_report_step_id(
                        report_summary["stat"]["response_time"]["slow"])
                    report_summary["stat"]["response_time"][
                        "very_slow"] = await ApiReportStep.get_element_id_by_report_step_id(
                        report_summary["stat"]["response_time"]["very_slow"])
                await self.send_report_if_task([{"report_id": report_id, "report_summary": report_summary}])
                await self.update_record_to_report()  # 覆盖之前的执行结果（如有需要）

            else:  # 合并通知
                # 获取当前批次下的所有测试报告，summary
                query_res = await self.report_model.filter(batch_id=self.report.batch_id).all().values("id", "summary")
                send_list = []
                if self.run_type == "api":  # 接口自动化，为了报告的精准性，慢接口的统计精确到接口个数
                    for query in query_res:
                        summary = query[1]
                        summary["stat"]["response_time"]["slow"] = await ApiReportStep.get_element_id_by_report_step_id(summary["stat"]["response_time"]["slow"])
                        summary["stat"]["response_time"]["very_slow"] = await ApiReportStep.get_element_id_by_report_step_id(summary["stat"]["response_time"]["very_slow"])
                        send_list.append({"report_id": query["id"], "report_summary": summary})
                else:
                    send_list = [{"report_id": query["id"], "report_summary": query["summary"]} for query in query_res]
                await self.send_report_if_task(send_list)

    async def update_record_to_report(self):
        """ 仅用于重跑！！如果指定了要插入的报告，则把当前执行的报告下的用例和步骤插入到对应的数据 """
        if self.insert_to:
            for case_id in self.report.trigger_id:
                # 更新report_case
                current_report_case = await self.report_case_model.filter(report_id=self.report.id,case_id=case_id).first()
                update_report_case = await self.report_case_model.filter(report_id=self.insert_to, case_id=case_id).first().values("id")
                await self.report_case_model.filter(report_id=self.insert_to, case_id=case_id).update(
                    result=current_report_case.result, case_data=current_report_case.case_data,
                    summary=current_report_case.summary, error_msg=current_report_case.error_msg
                )

                # 插入report_step
                # 为了问题溯源，需要保留原有的步骤数据，所以全量插入新的测试步骤到该用例下
                report_step_id_list = await self.report_step_model.filter(report_id=self.report.id,report_case_id=current_report_case.id).all().values("id")
                # 插入一个空步骤，作为重跑标识
                await self.report_step_model.model_create(dict(
                    report_id=self.insert_to, report_case_id=update_report_case["id"], case_id=case_id,
                    step_id=0, element_id=0, name=f"{'*' * 20} 以下步骤为重跑产生, 来自报告: 【{self.report.id}】 {'*' * 20}"
                ))
                for report_step_id in report_step_id_list:
                    current_report_step = await self.report_step_model.filter(id=report_step_id["id"]).first()
                    new_data = dict(current_report_step)
                    new_data["report_id"], new_data["report_case_id"] = self.insert_to, update_report_case["id"]
                    await self.report_step_model.model_create(new_data)

            # 更新report
            update_summary = await self.report_model.filter(id=self.insert_to).first().values("summary")
            update_summary["summary"]["stat"]["test_case"]["fail"] -= self.report.summary["stat"]["test_case"]["success"]
            update_summary["summary"]["stat"]["test_case"]["success"] += self.report.summary["stat"]["test_case"]["success"]
            update_summary["summary"]["result"] = self.report.summary["result"]  # 更新测试结果
            await self.report_model.filter(id=self.insert_to).update(
                summary=update_summary["summary"], is_passed=self.report.is_passed, notified=False  # 状态更新后未通知
            )

    async def run_case(self):
        """ 调 testRunner().run() 执行测试 """
        logger.info(f'\n测试执行数据：\n{self.test_plan}')

        if self.test_plan.get("is_async", 0):
            # 并行执行, 遍历case，以case为维度多线程执行，测试报告按顺序排列
            run_case_res_dict = {}
            await self.report.run_case_start()
            for index, case in enumerate(self.test_plan["report_case_list"]):
                run_case_res_dict[index] = False  # 用例运行标识，索引：是否运行完成
                test_plan = copy.deepcopy(self.test_plan)
                test_plan["report_case_list"] = [case]
                # self._async_run_case(temp_case, run_case_dict, index) # TODO 并行执行
        else:  # 串行执行
            await self.sync_run_case()

    async def sync_run_case(self):
        """ 单线程运行用例 """
        await self.report.run_case_start()
        runner = TestRunner()
        await runner.run(self.test_plan)
        await self.report.run_case_finish()
        logger.info(f'测试执行完成，开始保存测试报告和发送报告')
        summary = runner.summary
        summary["stat"]["count"]["step"] = self.count_step
        summary["stat"]["count"]["api"] = len(self.api_set)
        summary["stat"]["count"]["element"] = len(self.element_set)
        if self.run_type == "api":
            summary["stat"]["response_time"]["response_time_level"] = self.test_plan["response_time_level"]
        await self.save_report_and_send_message(summary)

    async def send_report_if_task(self, notify_list):
        """ 发送测试报告 """
        # 非任务 或者 触发方式为页面 或者 状态为中断，均不发通知
        if self.task_dict and self.report.trigger_type != TriggerTypeEnum.PAGE:
            await self.call_back_to_pipeline(notify_list)  # 回调流水线

            # 中断测试的不发送通知
            if await self.report_step_model.filter(report_id=self.report.id, status=ReportStepStatusEnum.STOP).first().values("id"):
                return

            if self.task_dict["receive_type"] == ReceiveTypeEnum.EMAIL:  # 邮件
                email_server = await Config.filter(name=self.task_dict["email_server"]).first().values("value")
                self.task_dict["email_server"] = email_server["value"]
                email_from = await User.filter(id=self.task_dict["email_from"]).first().values("email", "email_password")
                self.task_dict["email_from"], self.task_dict["email_pwd"] = email_from["email"], email_from["email_password"]
                email_to = await User.filter(id__in=self.task_dict["email_to"]).all().values("email")
                self.task_dict["email_to"] = [email["email"] for email in email_to]
            else:  # 解析并组装webhook地址并加签
                self.task_dict["webhook_list"] = await WebHook.get_webhook_list(
                    self.task_dict["receive_type"], self.task_dict["webhook_list"])

            res = await send_report(content_list=notify_list, **self.task_dict, report_addr=self.front_report_addr)
            if res is True:
                await self.report.model_update({"notified": True})

    async def call_back_to_pipeline(self, notify_list):
        """ 如果是流水线触发的，则回调给流水线 """
        if self.report.trigger_type == TriggerTypeEnum.PIPELINE:
            all_res = [notify["report_summary"]["result"] for notify in notify_list]
            await call_back_for_pipeline(
                self.task_dict["id"],
                self.task_dict["call_back"] or [],
                self.extend,
                "fail" if "fail" in all_res else "success"
            )

    async def push_hit_if_fail(self, result):
        """ 如果测试为不通过，且设置了要自动保存问题记录，且处罚类型为定时任务或者流水线触发，则保存 """
        if self.task_dict:
            # logger.info(f'开始保存问题记录')
            if (result == "fail" and self.task_dict["push_hit"] == 1
                    and self.report.trigger_type in [TriggerTypeEnum.CRON, TriggerTypeEnum.PIPELINE]):
                await Hits.model_create({
                    "hit_type": "巡检不通过",
                    "hit_detail": "",
                    "test_type": self.run_type,
                    "project_id": self.report.project_id,
                    "env": self.env_code,
                    "record_from": 2,  # 自动记录
                    "report_id": self.report.id,
                    "desc": "自动化测试创建"
                })

    @staticmethod
    def parse_api(project, api):
        """ 把解析后的接口对象 解析为testRunner的数据结构 """
        return {
            "id": api.id,
            "name": api.name,  # 接口名
            "skip": "",  # 无条件跳过当前测试
            "skip_if": "",  # 如果条件为真，则跳过当前测试
            "skip_unless": "",  # 除非条件为真，否则跳过当前测试
            "times": 1,  # 运行次数
            "extract": api.extracts,  # 接口要提取的信息
            "validate": api.validates,  # 接口断言信息
            "base_url": project.host,
            "body_type": api.body_type,
            "variables": [],
            "request": {
                "method": api.method,
                "url": api.addr,
                "timeout": api.time_out,
                "headers": api.headers,  # 接口头部信息
                "params": api.params,  # 接口查询字符串参数
                "json": api.data_json,
                "data": api.data_form,
                "files": api.data_file
            }
        }

    @staticmethod
    def build_summary(source1, source2, field_list):
        """ 合并测试报告统计 """
        for field in field_list:
            for key in source1["stat"][field]:
                source1["stat"][field][key] += source2["stat"][field][key]
