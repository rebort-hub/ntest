"""
aitestrebort 全局配置管理路由
"""
from ..base_view import APIRouter
from ...services.aitestrebort import global_config as global_service

router = APIRouter()

# LLM 配置管理
router.add_get_route("/global/llm-configs", global_service.get_llm_configs, summary="获取LLM配置列表")
router.add_post_route("/global/llm-configs", global_service.create_llm_config, summary="创建LLM配置")
router.add_put_route("/global/llm-configs/{config_id}", global_service.update_llm_config, summary="更新LLM配置")
router.add_delete_route("/global/llm-configs/{config_id}", global_service.delete_llm_config, summary="删除LLM配置")
router.add_post_route("/global/llm-configs/{config_id}/test", global_service.test_llm_config, summary="测试LLM配置")

# MCP 配置管理
router.add_get_route("/global/mcp-configs", global_service.get_mcp_configs, summary="获取MCP配置列表")
router.add_post_route("/global/mcp-configs", global_service.create_mcp_config, summary="创建MCP配置")
router.add_put_route("/global/mcp-configs/{config_id}", global_service.update_mcp_config, summary="更新MCP配置")
router.add_delete_route("/global/mcp-configs/{config_id}", global_service.delete_mcp_config, summary="删除MCP配置")

# API 密钥管理
router.add_get_route("/global/api-keys", global_service.get_api_keys, summary="获取API密钥列表")
router.add_post_route("/global/api-keys", global_service.create_api_key, summary="创建API密钥")
router.add_put_route("/global/api-keys/{key_id}", global_service.update_api_key, summary="更新API密钥")
router.add_delete_route("/global/api-keys/{key_id}", global_service.delete_api_key, summary="删除API密钥")

# LLM 对话管理
router.add_get_route("/global/conversations", global_service.get_conversations, summary="获取对话列表")
router.add_post_route("/global/conversations", global_service.create_conversation, summary="创建对话")
router.add_put_route("/global/conversations/{conversation_id}", global_service.update_conversation, summary="更新对话")
router.add_delete_route("/global/conversations/{conversation_id}", global_service.delete_conversation, summary="删除对话")
router.add_post_route("/global/conversations/batch-delete", global_service.batch_delete_conversations, summary="批量删除对话")
router.add_get_route("/global/conversations/{conversation_id}/messages", global_service.get_conversation_messages, summary="获取对话消息")
router.add_post_route("/global/conversations/{conversation_id}/messages", global_service.send_message, summary="发送消息")
router.add_delete_route("/global/conversations/{conversation_id}/messages", global_service.clear_conversation_messages, summary="清空对话消息")
router.add_get_route("/global/conversations/{conversation_id}/export", global_service.export_conversation, summary="导出对话")

# 流式对话
from app.services.aitestrebort import conversation_stream
router.add_post_route(
    "/global/conversations/{conversation_id}/messages/stream", 
    conversation_stream.send_message_stream, 
    summary="流式发送消息",
    response_model=None  # 流式响应不需要response_model
)

# 提示词管理
from app.services.aitestrebort import prompt as prompt_service
router.add_get_route("/global/prompts", prompt_service.get_prompts, summary="获取提示词列表")
router.add_post_route("/global/prompts", prompt_service.create_prompt, summary="创建提示词")
router.add_put_route("/global/prompts/{prompt_id}", prompt_service.update_prompt, summary="更新提示词")
router.add_delete_route("/global/prompts/{prompt_id}", prompt_service.delete_prompt, summary="删除提示词")
router.add_get_route("/global/prompts/default", prompt_service.get_default_prompt, summary="获取默认提示词")
router.add_get_route("/global/prompts/by-type", prompt_service.get_prompt_by_type, summary="根据类型获取提示词")
router.add_get_route("/global/prompts/types", prompt_service.get_prompt_types, summary="获取提示词类型")
router.add_post_route("/global/prompts/{prompt_id}/set-default", prompt_service.set_default_prompt, summary="设置默认提示词")
router.add_post_route("/global/prompts/clear-default", prompt_service.clear_default_prompt, summary="清除默认提示词")
router.add_post_route("/global/prompts/{prompt_id}/duplicate", prompt_service.duplicate_prompt, summary="复制提示词")
