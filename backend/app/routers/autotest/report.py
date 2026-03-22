from ..base_view import APIRouter
from ...services.autotest import report as service

report_router = APIRouter()

report_router.add_get_route("/list", service.get_report_list, summary="获取测试报告列表")
report_router.add_get_route("/status", service.get_report_status, auth=False, summary="根据运行id获取当次报告是否全部生成")
report_router.add_get_route("/show-id", service.get_report_show_id, auth=False, summary="根据运行id获取当次要打开的报告")
report_router.add_post_route("/notify", service.notify_report, auth=True, summary="手动触发报告通知，仅限任务，且为未通知的")
report_router.add_post_route(
    "/as-case", service.save_report_as_case, summary="保存报告中的接口为用例（仅报告运行类型为接口使用）")
report_router.add_get_route("", service.get_report_detail, auth=False, summary="获取测试报告")
report_router.add_delete_route("", service.delete_report, summary="删除测试报告主数据")
report_router.add_get_route("/case-list", service.get_report_case_list, auth=False, summary="获取报告的用例列表")
report_router.add_get_route("/suite-list", service.get_report_suite_list, auth=False, summary="获取报告的用例集列表")
report_router.add_get_route("/case", service.get_report_case, auth=False, summary="获取报告的用例数据")
report_router.add_get_route(
    "/rerun-case", service.get_report_rerun_case_list, auth=False, summary="获取此报告下指定结果的用例id")
report_router.add_get_route("/step-list", service.get_report_step_list, auth=False, summary="获取报告的步骤列表")
report_router.add_get_route("/step", service.get_report_step, auth=False, summary="获取报告的步骤数据")
report_router.add_put_route(
    "/step-status", service.change_report_step_status, auth=False, summary="修改步骤的状态，控制模拟debug")
report_router.add_get_route("/step-img", service.get_report_step_img, auth=False, summary="获取报告的步骤截图")
report_router.add_get_route("/report-clear", service.report_clear, auth=False, summary="清除测试报告")
