"""
aitestrebort 项目管理路由
"""
from ..base_view import APIRouter
from ...services.aitestrebort import project as project_service

router = APIRouter()

"""
aitestrebort 项目管理路由
"""
from ..base_view import APIRouter
from ...services.aitestrebort import project as project_service

router = APIRouter()

# 基础项目管理路由
router.add_get_route("/test", project_service.test_simple, auth=False, summary="测试接口")
router.add_get_route("/projects", project_service.get_projects, summary="获取项目列表")
router.add_post_route("/projects", project_service.create_project, summary="创建项目")
router.add_get_route("/projects/{project_id}", project_service.get_project_detail, summary="获取项目详情")
router.add_put_route("/projects/{project_id}", project_service.update_project, summary="更新项目")
router.add_delete_route("/projects/{project_id}", project_service.delete_project, summary="删除项目")
router.add_get_route("/projects/{project_id}/statistics", project_service.get_project_statistics, summary="获取项目统计信息")

# 项目凭据管理路由
router.add_get_route("/projects/{project_id}/credentials", project_service.get_project_credentials, summary="获取项目凭据列表")
router.add_post_route("/projects/{project_id}/credentials", project_service.create_project_credential, summary="创建项目凭据")

# 项目成员管理路由
router.add_get_route("/projects/{project_id}/members", project_service.get_project_members, summary="获取项目成员列表")
router.add_post_route("/projects/{project_id}/members", project_service.add_project_member, summary="添加项目成员")
router.add_delete_route("/projects/{project_id}/members/{member_id}", project_service.remove_project_member, summary="移除项目成员")

# LLM 配置管理路由
router.add_get_route("/projects/{project_id}/llm-configs", project_service.get_llm_configs, summary="获取LLM配置列表")
router.add_post_route("/projects/{project_id}/llm-configs", project_service.create_llm_config, summary="创建LLM配置")
router.add_put_route("/projects/{project_id}/llm-configs/{config_id}", project_service.update_llm_config, summary="更新LLM配置")
router.add_delete_route("/projects/{project_id}/llm-configs/{config_id}", project_service.delete_llm_config, summary="删除LLM配置")

# MCP 配置管理路由
router.add_get_route("/projects/{project_id}/mcp-configs", project_service.get_mcp_configs, summary="获取MCP配置列表")
router.add_post_route("/projects/{project_id}/mcp-configs", project_service.create_mcp_config, summary="创建MCP配置")
router.add_put_route("/projects/{project_id}/mcp-configs/{config_id}", project_service.update_mcp_config, summary="更新MCP配置")
router.add_delete_route("/projects/{project_id}/mcp-configs/{config_id}", project_service.delete_mcp_config, summary="删除MCP配置")
router.add_post_route("/projects/{project_id}/mcp-configs/{config_id}/test", project_service.test_mcp_config, summary="测试MCP配置连接")

# API 密钥管理路由
router.add_get_route("/projects/{project_id}/api-keys", project_service.get_api_keys, summary="获取API密钥列表")
router.add_post_route("/projects/{project_id}/api-keys", project_service.create_api_key, summary="创建API密钥")
router.add_put_route("/projects/{project_id}/api-keys/{key_id}", project_service.update_api_key, summary="更新API密钥")
router.add_delete_route("/projects/{project_id}/api-keys/{key_id}", project_service.delete_api_key, summary="删除API密钥")
router.add_post_route("/projects/{project_id}/api-keys/{key_id}/test", project_service.test_api_key, summary="测试API密钥")
router.add_post_route("/projects/{project_id}/api-keys/{key_id}/regenerate", project_service.regenerate_api_key, summary="重新生成API密钥")

# LLM 对话管理路由
router.add_get_route("/projects/{project_id}/conversations", project_service.get_conversations, summary="获取对话列表")
router.add_post_route("/projects/{project_id}/conversations", project_service.create_conversation, summary="创建对话")
router.add_get_route("/projects/{project_id}/conversations/{conversation_id}/messages", project_service.get_conversation_messages, summary="获取对话消息")
router.add_post_route("/projects/{project_id}/conversations/{conversation_id}/messages", project_service.send_message, summary="发送消息")
router.add_delete_route("/projects/{project_id}/conversations/{conversation_id}", project_service.delete_conversation, summary="删除对话")

# 提示词管理路由
router.add_get_route("/projects/{project_id}/prompts", project_service.get_prompts, summary="获取提示词列表")

# 知识库管理路由（代理到知识库服务）
router.add_get_route("/projects/{project_id}/knowledge-bases", project_service.get_knowledge_bases, summary="获取知识库列表")