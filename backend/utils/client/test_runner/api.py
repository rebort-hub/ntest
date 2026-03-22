import datetime
import traceback

from utils.logs.log import logger
from . import exceptions, parser, runner


class TestRunner:

    def __init__(self):
        self.summary = None

    async def run_test(self, parsed_tests_mapping):
        """ 执行测试 """
        functions = parsed_tests_mapping.get("project_mapping", {}).get("functions", {})
        report_case_model = parsed_tests_mapping.get("report_case_model")
        report_step_model = parsed_tests_mapping.get("report_step_model")
        test_case_mapping = parsed_tests_mapping["test_case_mapping"]  # 执行测试用例

        report_case = await report_case_model.filter(id=test_case_mapping["config"]["report_case_id"]).first()
        case_runner = runner.Runner(test_case_mapping["config"], functions)
        await case_runner.init_session_context()

        report_case.summary["stat"]["total"] = len(test_case_mapping["step_list"])
        await report_case.test_is_running()

        report_case.summary["time"]["start_at"] = datetime.datetime.now()  # 开始执行用例时间
        for test_step in test_case_mapping["step_list"]:
            try:
                await case_runner.run_step(test_step, report_step_model)  # 执行测试步骤
                step_error_traceback = None
            except Exception as error:
                step_error_traceback = traceback.format_exc()

                # 没有执行结果，代表是执行异常，否则代表是步骤里面捕获了异常过后再抛出来的
                if case_runner.client_session.meta_data["result"] is None:
                    logger.error(traceback.format_exc())
                    case_runner.client_session.meta_data["result"] = "error"

            await case_runner.report_step.save_step_result_and_summary(case_runner, step_error_traceback)
            if case_runner.run_type == "api":
                case_runner.report_step.add_run_step_result_count(report_case.summary, case_runner.client_session.meta_data, parsed_tests_mapping["response_time_level"], test_step["report_step_id"])
            else:
                case_runner.report_step.add_run_step_result_count(report_case.summary, case_runner.client_session.meta_data)
        report_case.summary["time"]["end_at"] = datetime.datetime.now()  # 用例执行结束时间
        case_runner.try_close_browser()  # 执行完一条用例，不管是不是ui自动化，都强制执行关闭浏览器，防止执行时报错，导致没有关闭到浏览器造成driver进程一直存在
        await report_case.save_case_result_and_summary()

        return report_case.summary

    async def run(self, test_plan):
        """ 执行测试的流程 """
        report = await test_plan["report_model"].filter(id=test_plan["report_id"]).first()
        self.summary = report.summary  # 防止任务中没有用例导致报错
        start_run_test_time = datetime.datetime.now()
        for report_case_id in test_plan["report_case_list"]: # 解析一条用例就执行一条用例，减少内存开销
            parsed_test_res = await parser.parse_test_data(test_plan, report_case_id)  # 解析测试计划
            if parsed_test_res.get("result") == "error":  # 解析测试计划报错了，会返回当前用例的初始summary
                case_summary = parsed_test_res
            else:
                case_summary = await self.run_test(parsed_test_res)  # 执行测试用例
            self.summary = report.merge_test_result(case_summary)  # 汇总测试结果
        run_case_finish_time = datetime.datetime.now()
        self.summary["time"]["start_at"] = start_run_test_time.strftime("%Y-%m-%d %H:%M:%S")
        self.summary["time"]["end_at"] = run_case_finish_time.strftime("%Y-%m-%d %H:%M:%S")
        self.summary["time"]["all_duration"] = (run_case_finish_time - start_run_test_time).total_seconds()
