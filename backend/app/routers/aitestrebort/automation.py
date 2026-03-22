"""
aitestrebort 自动化脚本管理路由
"""
from ..base_view import APIRouter
from ...services.aitestrebort import automation as automation_service

router = APIRouter()

# 注册路由
router.add_get_route("/test-automation", automation_service.test_simple, summary="自动化脚本测试接口")

# 自动化脚本管理
router.add_get_route("/projects/{project_id}/automation-scripts", automation_service.get_automation_scripts, summary="获取自动化脚本列表")
router.add_post_route("/projects/{project_id}/automation-scripts", automation_service.create_automation_script, summary="创建自动化脚本")
router.add_get_route("/projects/{project_id}/automation-scripts/{script_id}", automation_service.get_automation_script_detail, summary="获取自动化脚本详情")
router.add_put_route("/projects/{project_id}/automation-scripts/{script_id}", automation_service.update_automation_script, summary="更新自动化脚本")
router.add_delete_route("/projects/{project_id}/automation-scripts/{script_id}", automation_service.delete_automation_script, summary="删除自动化脚本")

# 脚本执行管理
router.add_post_route("/projects/{project_id}/automation-scripts/{script_id}/execute", automation_service.execute_automation_script, summary="执行自动化脚本")
router.add_get_route("/projects/{project_id}/automation-scripts/{script_id}/executions", automation_service.get_script_executions, summary="获取脚本执行历史")
router.add_get_route("/projects/{project_id}/automation-scripts/{script_id}/executions/{execution_id}", automation_service.get_execution_detail, summary="获取执行详情")