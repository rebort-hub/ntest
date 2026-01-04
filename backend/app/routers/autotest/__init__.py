from ..base_view import APIRouter

api_test = APIRouter()
from app.routers.autotest.project import project_router
from app.routers.autotest.module import module_router
from app.routers.autotest.api import api_router
from app.routers.autotest.suite import suite_router
from app.routers.autotest.case import case_router
from app.routers.autotest.step import step_router
from app.routers.autotest.task import task_router
from app.routers.autotest.report import report_router
from app.routers.autotest.dashboard import dashboard_router
from app.routers.autotest.stat import stat_router
api_test.include_router(project_router, prefix="/project", tags=["服务管理"])
api_test.include_router(module_router, prefix="/module", tags=["模块管理"])
api_test.include_router(api_router, prefix="/api", tags=["接口管理"])
api_test.include_router(suite_router, prefix="/suite", tags=["用例集管理"])
api_test.include_router(case_router, prefix="/case", tags=["用例管理"])
api_test.include_router(step_router, prefix="/step", tags=["步骤管理"])
api_test.include_router(task_router, prefix="/task", tags=["任务管理"])
api_test.include_router(report_router, prefix="/report", tags=["报告管理"])
api_test.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_test.include_router(stat_router, prefix="/stat", tags=["stat"])


app_test = APIRouter()
from app.routers.autotest.project import project_router
from app.routers.autotest.module import module_router
from app.routers.autotest.page import page_router
from app.routers.autotest.element import element_router
from app.routers.autotest.suite import suite_router
from app.routers.autotest.case import case_router
from app.routers.autotest.step import step_router
from app.routers.autotest.task import task_router
from app.routers.autotest.report import report_router
from app.routers.autotest.device import device_router
app_test.include_router(project_router, prefix="/project", tags=["服务管理"])
app_test.include_router(module_router, prefix="/module", tags=["模块管理"])
app_test.include_router(page_router, prefix="/page", tags=["页面管理"])
app_test.include_router(element_router, prefix="/element", tags=["元素管理"])
app_test.include_router(suite_router, prefix="/suite", tags=["用例集管理"])
app_test.include_router(case_router, prefix="/case", tags=["用例管理"])
app_test.include_router(step_router, prefix="/step", tags=["步骤管理"])
app_test.include_router(task_router, prefix="/task", tags=["任务管理"])
app_test.include_router(report_router, prefix="/report", tags=["报告管理"])
app_test.include_router(device_router, prefix="/device", tags=["设备管理"])


ui_test = APIRouter()
from app.routers.autotest.project import project_router
from app.routers.autotest.module import module_router
from app.routers.autotest.page import page_router
from app.routers.autotest.element import element_router
from app.routers.autotest.suite import suite_router
from app.routers.autotest.case import case_router
from app.routers.autotest.step import step_router
from app.routers.autotest.task import task_router
from app.routers.autotest.report import report_router
ui_test.include_router(project_router, prefix="/project", tags=["服务管理"])
ui_test.include_router(module_router, prefix="/module", tags=["模块管理"])
ui_test.include_router(page_router, prefix="/page", tags=["页面管理"])
ui_test.include_router(element_router, prefix="/element", tags=["元素管理"])
ui_test.include_router(suite_router, prefix="/suite", tags=["用例集管理"])
ui_test.include_router(case_router, prefix="/case", tags=["用例管理"])
ui_test.include_router(step_router, prefix="/step", tags=["步骤管理"])
ui_test.include_router(task_router, prefix="/task", tags=["任务管理"])
ui_test.include_router(report_router, prefix="/report", tags=["报告管理"])
