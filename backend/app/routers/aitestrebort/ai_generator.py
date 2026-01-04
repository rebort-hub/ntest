"""
aitestrebort AI 生成器路由
"""
from ..base_view import APIRouter
from ...services.aitestrebort import ai_generator as ai_service

router = APIRouter()

# 基础测试接口
router.add_get_route("/test-ai", ai_service.test_simple, summary="AI生成器测试接口")

# AI 测试用例生成
router.add_post_route("/projects/{project_id}/ai/generate-testcase", ai_service.generate_testcase_from_requirement, summary="根据需求生成测试用例")
router.add_post_route("/projects/{project_id}/ai/generate-conversation", ai_service.generate_testcase_conversation_api, summary="对话式生成测试用例")
router.add_post_route("/projects/{project_id}/ai/save-testcases", ai_service.save_generated_testcases, summary="保存生成的测试用例")
router.add_put_route("/projects/{project_id}/testcases/{testcase_id}/optimize", ai_service.optimize_existing_testcase, summary="优化现有测试用例")
router.add_post_route("/projects/{project_id}/ai/generate-from-screenshot", ai_service.generate_testcase_from_screenshot, summary="根据截图生成测试用例")
router.add_post_route("/projects/{project_id}/ai/batch-generate", ai_service.batch_generate_testcases, summary="批量生成测试用例")

# 需求来源管理
router.add_get_route("/projects/{project_id}/ai/requirement-sources", ai_service.get_requirement_sources, summary="获取需求来源列表")
router.add_post_route("/projects/{project_id}/ai/requirement-sources", ai_service.create_requirement_source, summary="创建需求来源")
router.add_get_route("/projects/{project_id}/ai/requirement-sources/{source_id}/content", ai_service.get_requirement_source_content, summary="获取需求来源内容")

# AI 自动化脚本生成
router.add_post_route("/projects/{project_id}/testcases/{testcase_id}/generate-script", ai_service.generate_automation_script_from_testcase, summary="从测试用例生成自动化脚本")

# AI 生成历史
router.add_get_route("/projects/{project_id}/ai/generation-history", ai_service.get_generation_history, summary="获取AI生成历史记录")