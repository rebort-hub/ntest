from ..base_view import APIRouter
from ...services.autotest import stat as service

stat_router = APIRouter()

stat_router.add_get_route("/use-card", service.get_use_card, summary="使用统计卡片")
stat_router.add_get_route("/use-chart", service.get_use_chart, summary="使用统计图表")
stat_router.add_get_route("/analyse", service.get_report_chart, summary="获取测试报告维度统计")
