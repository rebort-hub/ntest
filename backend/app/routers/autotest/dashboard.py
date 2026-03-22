from ..base_view import APIRouter
from ...services.autotest import dashboard as service

dashboard_router = APIRouter()

dashboard_router.add_get_route("/card", service.get_api_test_title, auth=False, summary="获取卡片统计")
dashboard_router.add_get_route("/project", service.get_api_test_project, auth=False, summary="统计服务数")
dashboard_router.add_get_route("/module", service.get_api_test_module, auth=False, summary="统计模块数")
dashboard_router.add_get_route("/api", service.get_api_test_api, auth=False, summary="统计接口数")
dashboard_router.add_get_route("/case", service.get_api_test_case, auth=False, summary="统计用例数")
dashboard_router.add_get_route("/step", service.get_api_test_step, auth=False, summary="统计步骤数")
dashboard_router.add_get_route("/task", service.get_api_test_task, auth=False, summary="统计定时任务数")
dashboard_router.add_get_route("/report", service.get_api_test_report, auth=False, summary="统计测试报告数")
