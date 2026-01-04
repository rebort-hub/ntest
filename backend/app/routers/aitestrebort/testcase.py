"""
aitestrebort 测试用例管理路由
"""
from ..base_view import APIRouter
from ...services.aitestrebort import testcase as testcase_service

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