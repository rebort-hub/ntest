# -*- coding: utf-8 -*-
from app.models.autotest.model_factory import ApiCaseSuite as CaseSuite, ApiMsg as Api, ApiStep as Step,\
    ApiReportCase as ReportCase, ApiReportStep as reportStep
from app.models.assist.model_factory import Script
from app.models.config.model_factory import Config
from app.schemas.enums import DataStatusEnum
from utils.client.parse_model import StepModel, FormatModel
from utils.client.run_test_runner import RunTestRunner
from utils.logs.log import logger

class RunApi(RunTestRunner):
    """ 接口调试 """

    def __init__(self, api_id_list, report_id, env_code, env_name):
        super().__init__(report_id=report_id, env_code=env_code, env_name=env_name, run_type="api")
        self.api_id_list = api_id_list  # 要执行的接口id
        self.project = {}  # 解析当前服务信息
        self.project = None  # 解析当前服务信息
        self.count_step = 1

    async def parse_and_run(self):
        """ 把解析放到异步线程里面 """
        self.time_out = await Config.get_request_time_out()
        self.test_plan["response_time_level"] = await Config.get_response_time_level()
        self.front_report_addr = f'{await Config.get_report_host()}{await Config.get_api_report_addr()}'
        self.test_plan["pause_step_time_out"] = await Config.get_pause_step_time_out()
        await Script.create_script_file(self.env_code)  # 创建所有函数文件
        self.report = await self.report_model.filter(id=self.report_id).first()
        self.project = await self.get_format_project(self.report.project_id)  # 解析当前服务信息
        await self.format_data_for_template()  # 解析api
        await self.report.parse_data_finish()
        await self.run_case()

    async def format_data_for_template(self):
        """ 接口调试 """
        logger.info(f'本次测试的接口id：{self.api_id_list}')

        # 解析api
        for api_id in self.api_id_list:
            api_dict = await self.get_format_api(self.project, api_id=api_id)

            # 记录解析下后的用例，单接口运行时，没有用例，为了统一数据结构，所以把接口视为一条用例
            report_case = await ReportCase.create(
                name=api_dict["name"],
                report_id=self.report.id,
                run_type="api",
                case_data={
                    "headers": {},
                    "run_times": 1,
                    "run_env": self.env_code,
                    "variables": self.project.variables
                    },
                summary=ReportCase.get_summary_template()
            )

            # 合并头部信息
            step_headers = {}
            step_headers.update(self.project.headers)
            step_headers.update(api_dict["request"]["headers"])
            api_dict["request"]["headers"] = step_headers

            report_step = await reportStep.create(
                element_id=api_dict["id"],
                report_id=self.report.id,
                report_case_id=report_case.id,
                name=api_dict["name"],
                step_data=api_dict
            )
            api_dict["report_step"] = report_step
            self.test_plan["report_case_list"].append(report_case.id)
        self.init_parsed_data()


class RunCase(RunTestRunner):
    """ 运行测试用例 """

    def __init__(self, report_id, case_id_list, env_code, env_name, temp_variables={}, task_dict={}, is_async=0,
                 extend={}, insert_to=None, **kwargs):

        super().__init__(report_id=report_id, env_code=env_code, env_name=env_name, run_type="api", task_dict=task_dict,
                         extend=extend, insert_to=insert_to)
        self.temp_variables = temp_variables
        self.test_plan["is_async"] = is_async
        self.case_id_list = case_id_list  # 要执行的用例id_list
        self.all_case_steps = []  # 所有测试步骤

    async def parse_and_run(self):
        """ 把解析放到异步线程里面 """
        self.time_out = await Config.get_request_time_out()
        self.test_plan["response_time_level"] = await Config.get_response_time_level()
        self.front_report_addr = f'{await Config.get_report_host()}{await Config.get_api_report_addr()}'
        self.test_plan["pause_step_time_out"] = await Config.get_pause_step_time_out()
        await Script.create_script_file(self.env_code)  # 创建所有函数文件
        self.report = await self.report_model.filter(id=self.report_id).first()
        await self.parse_all_case()
        await self.report.parse_data_finish()
        await self.run_case()

    async def parse_step(self, current_project, project, current_case, case, api, step, report_case_id):
        """ 解析测试步骤
        current_project: 当前用例所在的服务(解析后的)
        project: 当前步骤对应接口所在的服务(解析后的)
        current_case: 当前用例
        case: 被引用的case
        api: 解析后的api
        step: 原始step
        返回解析后的步骤 {}
        """
        # 解析头部信息，继承头部信息，接口所在服务、当前所在服务、用例、步骤
        step_headers = {}
        step_headers.update(project.headers)
        if case:
            step_headers.update(case.headers)
        step_headers.update(current_project.headers)
        # step_headers.update(api["request"]["headers"])
        step_headers.update(current_case.headers)
        step_headers.update(step.headers)

        # 如果步骤设置了不使用字段，则去掉
        for filed in step.pop_header_filed:
            if filed in step_headers:
                step_headers.pop(filed)

        step_data = {
            "case_id": step.case_id,
            "name": step.name,
            "setup_hooks": step.up_func,
            "teardown_hooks": step.down_func,
            "skip_if": step.skip_if,  # 如果条件为真，则当前步骤不执行
            "times": step.run_times,  # 运行次数
            "extract": step.extracts,  # 接口要提取的信息
            "validate": step.validates,  # 接口断言信息
            "base_url": current_project.host if step.replace_host == 1 else project.host,
            "request": {
                "method": api["request"]["method"],
                "url": api["request"]["url"],
                "timeout": step.time_out or api["request"]["timeout"] or self.time_out,
                "headers": step_headers,  # 接口头部信息
                "params": step.params,  # 接口查询字符串参数
                "json": step.data_json,
                "data": step.data_form,
                "files": step.data_file,
                "follow_redirects": step.allow_redirect # httpx的重定向字段
            }
        }
        await reportStep.create(
            element_id=api["id"],
            step_id=step.id,
            case_id=step.case_id,
            report_id=self.report.id,
            report_case_id=report_case_id,
            name=step_data["name"],
            step_data=step_data
        )

    async def get_all_steps(self, case_id: int):
        """ 解析引用的用例 """
        case = await self.get_format_case(case_id)

        if self.parse_case_is_skip(case.skip_if) is not True:  # 不满足跳过条件才解析
            step_list = await Step.filter(case_id=case.id, status=DataStatusEnum.ENABLE).order_by("num").all()
            for step in step_list:
                if step.quote_case:
                    await self.get_all_steps(step.quote_case)
                else:
                    self.all_case_steps.append(step)
                    self.count_step += 1
                    self.api_set.add(step.api_id)

    async def parse_all_case(self):
        """ 解析所有用例 """

        # 遍历要运行的用例
        for case_id in self.case_id_list:
            current_case = await self.get_format_case(case_id)
            if current_case is None:
                continue

            # 如果传了临时参数
            if self.temp_variables:
                current_case.variables = FormatModel().parse_variables(self.temp_variables.get("variables"))
                current_case.headers = FormatModel().parse_list_data(self.temp_variables.get("headers"))
                current_case.skip_if = FormatModel().parse_skip_if(self.temp_variables.get("skip_if"))
                current_case.run_times = self.temp_variables.get("run_times", 1)

            for case_index in range(current_case.run_times or 1):
                # 用例的公共变量设置了数据驱动
                data_driver_dict = current_case.variables.get("data_driver_dict", {"key": "", "value": []})
                if data_driver_dict["key"] == "":
                    data_driver_dict = {"key": "data", "value": ["nothing"]}

                for data_driver_index, data_driver_value in enumerate(data_driver_dict["value"]):
                    current_case.variables[data_driver_dict["key"]] = data_driver_value
                    case_name = f'{current_case.name}_{case_index + 1}' if current_case.run_times > 1 else current_case.name
                    case_name = f'{case_name}_{data_driver_index}' if data_driver_index > 0 else case_name

                    # 记录解析下后的用例
                    report_case_data = current_case.get_attr()
                    report_case_data["run_env"] = self.env_code

                    report_case = await ReportCase.create(
                        name=case_name,
                        case_id=current_case.id,
                        suite_id=current_case.suite_id,
                        report_id=self.report.id,
                        case_data=current_case.get_attr(),
                        summary=ReportCase.get_summary_template()
                    )

                    # 满足跳过条件则跳过
                    if self.parse_case_is_skip(current_case.skip_if) is True:
                        await report_case.test_is_skip()
                        continue

                    case_suite = await CaseSuite.filter(id=current_case.suite_id).first()
                    current_project = await self.get_format_project(case_suite.project_id)
                    await self.get_all_steps(case_id)  # 递归获取测试步骤（中间有可能某些测试步骤是引用的用例）

                    # 循环解析测试步骤
                    all_variables = {}  # 当前用例的所有公共变量
                    for step in self.all_case_steps:
                        step = StepModel(**dict(step))
                        step_case = await self.get_format_case(step.case_id)
                        api_temp = await Api.filter(id=step.api_id).first()
                        api_project = await self.get_format_project(api_temp.project_id)
                        api_data = await self.get_format_api(api_project, api_obj=api_temp)

                        if step.data_driver:  # 如果有step.data_driver，则说明是数据驱动， 此功能废弃
                            """
                            数据驱动格式
                            [
                                {"comment": "用例1描述", "data": "请求数据，支持参数化"},
                                {"comment": "用例2描述", "data": "请求数据，支持参数化"}
                            ]
                            """
                            for driver_data in step.data_driver:
                                # 数据驱动的 comment 字段，用于做标识
                                step.name += driver_data.get("comment", "")
                                step.params = step.params = step.data_json = step.data_form = driver_data.get("data", {})
                                await self.parse_step(current_project, api_project, current_case, step_case, api_data, step, report_case.id)
                        else:
                            await self.parse_step(current_project, api_project, current_case, step_case, api_data, step, report_case.id)

                        # 把服务和用例的的自定义变量留下来
                        all_variables.update(api_project.variables)
                        all_variables.update(step_case.variables)

                    # 更新当前服务+当前用例的自定义变量，最后以当前用例设置的自定义变量为准
                    all_variables.update(current_project.variables)
                    all_variables.update(current_case.variables)
                    report_case_data["variables"].update(all_variables)  # = all_variables
                    report_case_data["run_type"] = self.run_type
                    await report_case.update_report_case_data(report_case_data)

                    self.test_plan["report_case_list"].append(report_case.id)
                    self.all_case_steps = []  # 完整的解析完一条用例后，去除对应的解析信息

        # 去除服务级的公共变量，保证用步骤上解析后的公共变量
        self.test_plan["project_mapping"]["variables"] = {}
        self.init_parsed_data()
