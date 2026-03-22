"""
aitestrebort 测试用例管理路由
"""
from ..base_view import APIRouter
from ...services.aitestrebort import testcase as testcase_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# 基础测试接口
router.add_get_route("/test-testcase", testcase_service.test_simple, summary="测试用例测试接口")

# 测试用例模块管理
router.add_get_route("/projects/{project_id}/testcase-modules", testcase_service.get_testcase_modules, summary="获取测试用例模块树")
router.add_post_route("/projects/{project_id}/testcase-modules", testcase_service.create_testcase_module, summary="创建测试用例模块")
router.add_put_route("/projects/{project_id}/testcase-modules/{module_id}", testcase_service.update_testcase_module, summary="更新测试用例模块")
router.add_delete_route("/projects/{project_id}/testcase-modules/{module_id}", testcase_service.delete_testcase_module, summary="删除测试用例模块")

# 测试用例管理
router.add_get_route("/projects/{project_id}/testcases", testcase_service.get_testcases, summary="获取测试用例列表")
router.add_post_route("/projects/{project_id}/testcases", testcase_service.create_testcase, summary="创建测试用例")
router.add_get_route("/projects/{project_id}/testcases/{testcase_id}", testcase_service.get_testcase_detail, summary="获取测试用例详情")
router.add_put_route("/projects/{project_id}/testcases/{testcase_id}", testcase_service.update_testcase, summary="更新测试用例")
router.add_delete_route("/projects/{project_id}/testcases/{testcase_id}", testcase_service.delete_testcase, summary="删除测试用例")
router.add_post_route("/projects/{project_id}/testcases/{testcase_id}/copy", testcase_service.copy_testcase, summary="复制测试用例")

# 测试用例步骤管理
router.add_get_route("/projects/{project_id}/testcases/{testcase_id}/steps", testcase_service.get_testcase_steps, summary="获取测试用例步骤")
router.add_post_route("/projects/{project_id}/testcases/{testcase_id}/steps", testcase_service.create_testcase_step, summary="创建测试用例步骤")
router.add_put_route("/projects/{project_id}/testcases/{testcase_id}/steps/{step_id}", testcase_service.update_testcase_step, summary="更新测试用例步骤")
router.add_delete_route("/projects/{project_id}/testcases/{testcase_id}/steps/{step_id}", testcase_service.delete_testcase_step, summary="删除测试用例步骤")

# 测试用例截图管理
router.add_get_route("/projects/{project_id}/testcases/{testcase_id}/screenshots", testcase_service.get_testcase_screenshots, summary="获取测试用例截图")
router.add_post_route("/projects/{project_id}/testcases/{testcase_id}/screenshots", testcase_service.upload_testcase_screenshot, summary="上传测试用例截图")
router.add_delete_route("/projects/{project_id}/testcases/{testcase_id}/screenshots/{screenshot_id}", testcase_service.delete_testcase_screenshot, summary="删除测试用例截图")

# 测试套件管理
router.add_get_route("/projects/{project_id}/test-suites", testcase_service.get_test_suites, summary="获取测试套件列表")
router.add_post_route("/projects/{project_id}/test-suites", testcase_service.create_test_suite, summary="创建测试套件")
router.add_get_route("/projects/{project_id}/test-suites/{suite_id}", testcase_service.get_test_suite_detail, summary="获取测试套件详情")
router.add_put_route("/projects/{project_id}/test-suites/{suite_id}", testcase_service.update_test_suite, summary="更新测试套件")
router.add_delete_route("/projects/{project_id}/test-suites/{suite_id}", testcase_service.delete_test_suite, summary="删除测试套件")

# 测试套件执行
router.add_post_route("/projects/{project_id}/test-suites/{suite_id}/execute", testcase_service.execute_test_suite, summary="执行测试套件")
router.add_get_route("/projects/{project_id}/test-executions", testcase_service.get_test_executions, summary="获取测试执行记录")
router.add_get_route("/projects/{project_id}/test-executions/{execution_id}", testcase_service.get_execution_detail, summary="获取执行记录详情")
router.add_put_route("/projects/{project_id}/test-executions/{execution_id}/cancel", testcase_service.cancel_test_execution, summary="取消测试执行")

# 测试套件脚本管理
router.add_post_route("/projects/{project_id}/test-suites/{suite_id}/scripts", testcase_service.add_scripts_to_suite, summary="添加脚本到测试套件")
router.add_delete_route("/projects/{project_id}/test-suites/{suite_id}/scripts/{script_id}", testcase_service.remove_script_from_suite, summary="从测试套件移除脚本")
router.add_get_route("/projects/{project_id}/test-suites/{suite_id}/scripts", testcase_service.get_suite_scripts, summary="获取测试套件脚本列表")

# 测试用例导出
router.add_api_route("/projects/{project_id}/testcases/export/xmind", testcase_service.export_testcases_to_xmind, methods=["GET"], response_model=None, summary="导出测试用例为XMind格式")

# WebSocket对话路由
from fastapi import WebSocket, Query, WebSocketDisconnect, status
from ...services.aitestrebort.conversation_websocket import handle_websocket_conversation
from ...models.system.model_factory import User

@router.websocket("/projects/{project_id}/conversations/{conversation_id}/ws")
async def websocket_conversation_endpoint(
    websocket: WebSocket,
    project_id: int,
    conversation_id: int,
    token: str = Query(None, description="访问令牌")
):
    """WebSocket对话端点
    
    Args:
        websocket: WebSocket连接
        project_id: 项目ID
        conversation_id: 对话ID
        token: JWT访问令牌（通过query参数传递）
    """
    # 从token中获取用户信息
    user_id = 1  # 默认用户ID
    
    if token:
        # 验证token并获取用户信息
        user_info = User.check_token(token, websocket.app.conf.token_secret_key)
        if user_info and isinstance(user_info, dict):
            user_id = user_info.get("id", 1)
        else:
            # Token无效，拒绝连接
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return
    
    await handle_websocket_conversation(websocket, user_id, conversation_id, project_id)

