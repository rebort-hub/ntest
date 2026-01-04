# -*- coding: utf-8 -*-
import json

from app.models.config.config import Config
from app.schemas.enums import DataStatusEnum
from app.models.autotest.model_factory import UiCaseSuite, UiStep, UiReportStep, UiReportCase, AppCaseSuite, AppStep, AppReportStep, AppReportCase, AppRunPhone
from app.models.assist.model_factory import Script
from utils.client.run_test_runner import RunTestRunner
from utils.client.parse_model import StepModel, FormatModel
from utils.client.test_runner.utils import build_url
from utils.util.file_util import FileUtil
from config import ui_action_mapping_reverse


class RunCase(RunTestRunner):
    """ 运行测试用例 """
    def __init__(self, report_id, case_id_list, env_code, env_name, temp_variables={}, task_dict={}, is_async=0,
                 extend={}, browser=True, appium_config={}, run_type="ui", **kwargs):

        super().__init__(report_id=report_id, env_code=env_code, env_name=env_name, run_type=run_type, extend=extend,
                         task_dict=task_dict)
        self.temp_variables = temp_variables
        self.run_type = run_type
        if run_type == "ui":
            self.suite_model = UiCaseSuite
            self.step_model = UiStep
            self.report_step_model = UiReportStep
            self.report_case_model = UiReportCase
            self.browser = browser
            self.device = self.device_id = self.run_server_id = self.run_phone_id = None
            self.device_dict = {}
            self.report_img_folder = FileUtil.make_img_folder_by_report_id(report_id, 'ui')
        else:
            self.suite_model = AppCaseSuite
            self.step_model = AppStep
            self.report_step_model = AppReportStep
            self.report_case_model = AppReportCase
            self.run_server_id = appium_config.pop("server_id")
            self.run_phone_id = appium_config.pop("phone_id")
            self.device = appium_config.pop("device")
            self.device_id = self.device["device_id"]
            self.device_dict = {}
            self.report_img_folder = FileUtil.make_img_folder_by_report_id(report_id, 'app')

        self.test_plan["is_async"] = is_async
        self.case_id_list = case_id_list  # 要执行的用例id_list
        self.appium_config = appium_config
        self.all_case_steps = []  # 所有测试步骤

    async def parse_and_run(self):
        """ 把解析放到异步线程里面 """
        self.wait_time_out = await Config.get_wait_time_out()
        if self.run_type == "ui":
            self.front_report_addr = f'{await Config.get_report_host()}{await Config.get_web_ui_report_addr()}'
        else:
            self.front_report_addr = f'{await Config.get_report_host()}{await Config.get_app_ui_report_addr()}'

        self.test_plan["pause_step_time_out"] = await Config.get_pause_step_time_out()
        await Script.create_script_file(self.env_code)  # 创建所有函数文件
        if self.run_type != "ui":
            self.device_dict = {device.id: dict(device) for device in await AppRunPhone.all()}
        self.report = await self.report_model.filter(id=self.report_id).first()
        await self.parse_all_case()
        await self.report.parse_data_finish()
        await self.run_case()

    async def parse_step(self, project, element, step, report_case_id):
        """ 解析测试步骤
        project: 当前步骤对应元素所在的项目(解析后的)
        element: 解析后的element
        step: 原始step
        返回解析后的步骤 {}
        """
        step_data = {
            "case_id": step.case_id,
            "name": step.name,
            "setup_hooks": step.up_func,
            "teardown_hooks": step.down_func,
            "skip_if": step.skip_if,  # 如果条件为真，则跳过当前测试
            "times": step.run_times,  # 运行次数
            "extract": step.extracts,  # 要提取的信息
            "validate": step.validates,  # 断言信息
            "test_action": {
                "execute_name": step.execute_name,
                "action": step.execute_type,
                "by_type": element.by,
                "screen": None if self.run_type == 'ui' else self.device_dict[element.template_device]["screen"],
                # 如果是打开页面，则设置为项目域名+页面地址
                "element": build_url(project.host, element.element) if element.by == "url" else element.element,
                "text": step.send_keys,
                "wait_time_out": float(step.wait_time_out or element.wait_time_out),
                "report_img_folder": self.report_img_folder  # 步骤截图的存放路径
            }
        }

        await self.report_step_model.create(
            element_id=element.id,
            step_id=step.id,
            case_id=step.case_id,
            report_id=self.report.id,
            report_case_id=step.report_case_id,
            name=step_data["name"],
            step_data=step_data
        )

    async def parse_extracts(self, extracts: list):
        """ 解析数据提取
        extracts_list:
            [
                {"data_source": "extract_09_value", "key": "name1", "remark": None, "value": 1},
                {"data_source": "func", "key": "name2", "remark": None, "value": "$do_something()"},
            ]
        return:
            [
                {
                    "type": "element",
                    "key": "name1",
                    "value": {
                        "action": "action_09get_value",
                        "by_type": "id",
                        "element": "su"
                    }
                },
                {"type": "func", "key": "name2", "value": "$do_something()"},
            ]
        """
        parsed_list = []
        for extract in extracts:
            if extract["extract_type"] in ("const", "func", "variable"):  # 自定义函数、变量提取、常量
                parsed_list.append({
                    "type": extract["extract_type"],
                    "key": extract.get("key"),
                    "value": extract.get("value")
                })
            elif extract["extract_type"]:  # 页面元素提取
                if extract["value"]:
                    element = await self.get_format_element(extract["value"])
                    parsed_list.append({
                        "type": "element",
                        "key": extract.get("key"),
                        "value": {
                            "action": extract.get("extract_type"),
                            "by_type": element.by,
                            "element": element.element
                        }
                    })
                else:
                    parsed_list.append({
                        "type": "element",
                        "key": extract.get("key"),
                        "value": {
                            "action": extract.get("extract_type")
                        }
                    })

        return parsed_list

    async def parse_validates(self, validates_list):
        """ 解析断言
        validates:
                [
                    {
                        '_01equals': ['variable.$a', '123']
                    },
                    {
                        'id': '1686479480568',
                        'validate_type': 'page',
                        'data_source': 3,
                        'key': None,
                        'validate_method': '相等',
                        'data_type': 'str',
                        'value': '234'
                    }
                ]
        return:
            [
                {          {
                    '_01equals': ['variable.$a', '123']
                },
                {
                    "comparator": "validate_type",  # 断言方式
                    "check": ("id", "kw"),  # 实际结果
                    "expect": "123123"  # 预期结果
                }
            ]
        """
        parsed_validate = []
        for validate in validates_list:
            if validate.get("data_source"):  # 页面断言，需要解析ui元素
                element = await self.get_format_element(validate["data_source"])
                parsed_validate.append({
                    "comparator": validate["validate_method"],  # 断言方式
                    "check": (element.by, element.element),  # 实际结果
                    "expect": self.build_expect_result(validate["data_type"], validate["value"])  # 预期结果
                })
            else:
                parsed_validate.append(validate)  # 已经解析过的数据断言
        return parsed_validate

    def build_expect_result(self, data_type, value):
        """ 生成预期结果 """
        if data_type in ["variable", "func", "str"]:
            return value
        elif data_type == "json":
            return json.dumps(json.loads(value))
        else:  # python数据类型
            return eval(f'{data_type}({value})')

    async def get_all_steps(self, case_id: int):
        """ 解析引用的用例 """
        case = await self.get_format_case(case_id)

        # 不满足跳过条件才解析
        if self.parse_case_is_skip(case.skip_if, self.run_server_id, self.run_phone_id) is not True:
            steps = await self.step_model.filter(case_id=case.id, status=DataStatusEnum.ENABLE).order_by("num").all()
            for step in steps:
                if step.quote_case:
                    await self.get_all_steps(step.quote_case)
                else:
                    self.all_case_steps.append(step)
                    self.count_step += 1
                    self.element_set.add(step.element_id)

    async def parse_all_case(self):
        """ 解析所有用例 """

        # 遍历要运行的用例
        for case_id in self.case_id_list:

            current_case = await self.get_format_case(case_id)
            if current_case is None:
                continue

            if self.temp_variables:
                current_case.variables = FormatModel().parse_variables(self.temp_variables.get("variables"))
                current_case.skip_if = FormatModel().parse_skip_if(self.temp_variables.get("skip_if"))
                current_case.run_times = self.temp_variables.get("run_times", 1)

            for index in range(current_case.run_times or 1):
                case_name = f'{current_case.name}_{index + 1}' if current_case.run_times > 1 else current_case.name

                # 记录解析下后的用例
                report_case_data = current_case.get_attr()
                report_case_data["run_env"] = self.env_code
                report_case = await self.report_case_model.create(
                    name=case_name,
                    case_id=current_case.id,
                    suite_id=current_case.suite_id,
                    report_id=self.report.id,
                    case_data=current_case.get_attr(),
                    summary=self.report_case_model.get_summary_template()
                )

                # 满足跳过条件则跳过
                if self.parse_case_is_skip(current_case.skip_if, self.run_server_id, self.run_phone_id) is True:
                    await report_case.test_is_skip()
                    continue

                case_suite = await self.suite_model.filter(id=current_case.suite_id).first()
                current_project = await self.get_format_project(case_suite.project_id)

                if self.run_type == 'ui':
                    # 用例格式模板, # 火狐：geckodriver
                    report_case_data["browser_type"] = self.browser
                    report_case_data["browser_path"] = FileUtil.get_driver_path(self.browser)
                else:
                    report_case_data["appium_config"] = self.appium_config

                await self.get_all_steps(case_id)  # 递归获取测试步骤（中间有可能某些测试步骤是引用的用例）

                # 循环解析测试步骤
                all_variables = {}  # 当前用例的所有公共变量
                for step in self.all_case_steps:
                    step_case = await self.get_format_case(step.case_id)
                    step_element = await self.get_format_element(step.element_id)
                    step = StepModel(**dict(step))
                    step.report_case_id = report_case.id
                    step.execute_name = ui_action_mapping_reverse[step.execute_type]  # 执行方式的别名，用于展示测试报告
                    step.extracts = await self.parse_extracts(step.extracts)  # 解析数据提取
                    step.validates = await self.parse_validates(step.validates)  # 解析断言
                    element_project = await self.get_format_project(step_element.project_id)  # 元素所在的项目

                    if step.data_driver:  # 如果有step.data_driver，则说明是数据驱动
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
                            await self.parse_step(element_project, step_element, step, report_case.id)

                    else:
                        await self.parse_step(element_project, step_element, step, report_case.id)

                    # 把服务和用例的的自定义变量留下来
                    all_variables.update(element_project.variables)
                    all_variables.update(step_case.variables)

                # 更新当前服务+当前用例的自定义变量，最后以当前用例设置的自定义变量为准
                all_variables.update(current_project.variables)
                all_variables.update(current_case.variables)
                all_variables.update({"device": self.device})  # 强制增加一个变量为设备id，用于去数据库查数据
                all_variables.update({"device_id": self.device_id})  # 强制增加一个变量为设备id，用于去数据库查数据
                report_case_data["variables"].update(all_variables)
                report_case_data["run_type"] = self.run_type
                await report_case.update_report_case_data(report_case_data)

                self.test_plan["report_case_list"].append(report_case.id)

                # 完整的解析完一条用例后，去除对应的解析信息
                self.all_case_steps = []

        # 去除服务级的公共变量，保证用步骤上解析后的公共变量
        self.test_plan["project_mapping"]["variables"] = {}
        self.init_parsed_data()
