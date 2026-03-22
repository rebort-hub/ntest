"""
aitestrebort 全局配置管理服务
注意：全局配置不关联项目（project_id为NULL）
"""
from typing import Optional
from fastapi import Request, Body
from tortoise.exceptions import DoesNotExist
from pydantic import BaseModel, Field

from app.models.aitestrebort import (
    aitestrebortLLMConfig, aitestrebortProject, aitestrebortProjectMember,
    aitestrebortConversation, aitestrebortMessage
)
from utils.logs.log import logger


# Schema定义
class LLMConfigCreateSchema(BaseModel):
    name: str = Field(..., description="模型名称")
    config_name: Optional[str] = Field(None, description="配置名称")
    provider: str = Field(..., description="LLM提供商")
    model_name: str = Field(..., description="模型名称")
    api_key: str = Field(..., description="API密钥")
    base_url: Optional[str] = Field(None, description="API基础URL")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    temperature: float = Field(0.7, description="温度参数")
    max_tokens: int = Field(2000, description="最大令牌数")
    supports_vision: bool = Field(False, description="是否支持多模态")
    context_limit: int = Field(128000, description="上下文限制")
    is_default: bool = Field(False, description="是否为默认配置")


# LLM 配置管理
async def get_llm_configs(request: Request):
    """获取LLM配置列表（全局配置，不关联项目）"""
    try:
        # 获取用户的全局配置（project_id为NULL的配置）
        configs = await aitestrebortLLMConfig.filter(
            creator_id=request.state.user.id,
            project_id=None
        ).order_by('-create_time').all()
        
        config_list = []
        for config in configs:
            config_data = {
                "id": config.id,
                "name": config.name,
                "config_name": config.config_name,
                "provider": config.provider,
                "model_name": config.model_name,
                "base_url": config.base_url,
                "system_prompt": config.system_prompt,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "supports_vision": config.supports_vision,
                "context_limit": config.context_limit,
                "is_default": config.is_default,
                "created_at": config.create_time
            }
            config_list.append(config_data)
        
        return request.app.get_success(data=config_list)
    except Exception as e:
        logger.error(f"Error in get_llm_configs: {str(e)}", exc_info=True)
        return request.app.error(msg=f"获取LLM配置列表失败: {str(e)}")


async def create_llm_config(request: Request, config_data: LLMConfigCreateSchema):
    """创建LLM配置"""
    try:
        # 如果设置为默认，先取消其他默认配置
        if config_data.is_default:
            await aitestrebortLLMConfig.filter(
                creator_id=request.state.user.id,
                project_id=None,
                is_default=True
            ).update(is_default=False)
        
        config = await aitestrebortLLMConfig.create(
            creator_id=request.state.user.id,
            project_id=None,  # 全局配置不关联项目
            name=config_data.name,
            config_name=config_data.config_name,
            provider=config_data.provider,
            model_name=config_data.model_name,
            api_key=config_data.api_key,
            base_url=config_data.base_url,
            system_prompt=config_data.system_prompt,
            temperature=config_data.temperature,
            max_tokens=config_data.max_tokens,
            supports_vision=config_data.supports_vision,
            context_limit=config_data.context_limit,
            is_default=config_data.is_default
        )
        
        return request.app.post_success(data={
            "id": config.id,
            "name": config.name,
            "config_name": config.config_name,
            "provider": config.provider,
            "model_name": config.model_name,
            "base_url": config.base_url,
            "system_prompt": config.system_prompt,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "supports_vision": config.supports_vision,
            "context_limit": config.context_limit,
            "is_default": config.is_default,
            "created_at": config.create_time
        })
    except Exception as e:
        logger.error(f"Error in create_llm_config: {str(e)}", exc_info=True)
        return request.app.error(msg=f"创建LLM配置失败: {str(e)}")


async def update_llm_config(request: Request, config_id: int, config_data: dict):
    """更新LLM配置"""
    try:
        config = await aitestrebortLLMConfig.get(
            id=config_id,
            creator_id=request.state.user.id,
            project_id=None
        )
        
        # 如果设置为默认，先取消其他默认配置
        if config_data.get('is_default') and not config.is_default:
            await aitestrebortLLMConfig.filter(
                creator_id=request.state.user.id,
                project_id=None,
                is_default=True
            ).update(is_default=False)
        
        # 更新字段
        for key, value in config_data.items():
            if hasattr(config, key) and value is not None:
                setattr(config, key, value)
        
        await config.save()
        
        return request.app.put_success(data={
            "id": config.id,
            "name": config.name,
            "provider": config.provider,
            "model_name": config.model_name,
            "base_url": config.base_url,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "is_default": config.is_default,
            "created_at": config.create_time
        })
    except DoesNotExist:
        return request.app.fail(msg="LLM配置不存在")
    except Exception as e:
        logger.error(f"Error in update_llm_config: {str(e)}", exc_info=True)
        return request.app.error(msg=f"更新LLM配置失败: {str(e)}")


async def delete_llm_config(request: Request, config_id: int):
    """删除LLM配置"""
    try:
        config = await aitestrebortLLMConfig.get(
            id=config_id,
            creator_id=request.state.user.id,
            project_id=None
        )
        await config.delete()
        return request.app.delete_success()
    except DoesNotExist:
        return request.app.fail(msg="LLM配置不存在")
    except Exception as e:
        logger.error(f"Error in delete_llm_config: {str(e)}", exc_info=True)
        return request.app.error(msg=f"删除LLM配置失败: {str(e)}")


async def test_llm_config(request: Request, config_id: int):
    """测试LLM配置"""
    try:
        # 导入真实的测试函数
        from .ai_generator_real import test_llm_config as real_test
        return await real_test(request, config_id)
    except Exception as e:
        logger.error(f"Error in test_llm_config: {str(e)}", exc_info=True)
        return request.app.error(msg=f"测试LLM配置失败: {str(e)}")


# MCP 配置管理 - 用户级别（全局）
async def get_mcp_configs(request: Request):
    """获取当前用户的 MCP 配置列表"""
    try:
        from ...models.aitestrebort.project import aitestrebortMCPConfig
        
        # 获取当前用户的所有 MCP 配置
        configs = await aitestrebortMCPConfig.filter(
            user_id=request.state.user.id
        ).order_by('-id')
        
        items = []
        for config in configs:
            items.append({
                "id": config.id,
                "name": config.name,
                "url": config.url,
                "transport": config.transport,
                "headers": config.headers,
                "created_at": config.create_time.strftime("%Y-%m-%d %H:%M:%S") if config.create_time else None
            })
        
        return request.app.get_success(data=items)
        
    except Exception as e:
        logger.error(f"获取 MCP 配置失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")

async def create_mcp_config(request: Request, config_data: dict):
    """创建 MCP 配置"""
    try:
        from ...models.aitestrebort.project import aitestrebortMCPConfig
        
        # 检查名称是否已存在
        if await aitestrebortMCPConfig.filter(
            user_id=request.state.user.id,
            name=config_data.get('name')
        ).exists():
            return request.app.fail(msg="配置名称已存在")
        
        config = await aitestrebortMCPConfig.create(
            user_id=request.state.user.id,
            name=config_data.get('name'),
            url=config_data.get('url'),
            transport=config_data.get('transport', 'sse'),
            headers=config_data.get('headers', {})
        )
        
        return request.app.post_success(data={
            "id": config.id,
            "name": config.name,
            "url": config.url
        })
        
    except Exception as e:
        logger.error(f"创建 MCP 配置失败: {str(e)}")
        return request.app.fail(msg=f"创建失败: {str(e)}")

async def update_mcp_config(request: Request, config_id: int, config_data: dict):
    """更新 MCP 配置"""
    try:
        from ...models.aitestrebort.project import aitestrebortMCPConfig
        
        config = await aitestrebortMCPConfig.get(
            id=config_id,
            user_id=request.state.user.id
        )
        
        # 更新字段
        if 'name' in config_data:
            config.name = config_data['name']
        if 'url' in config_data:
            config.url = config_data['url']
        if 'transport' in config_data:
            config.transport = config_data['transport']
        if 'headers' in config_data:
            config.headers = config_data['headers']
        
        await config.save()
        
        return request.app.put_success(data={
            "id": config.id,
            "name": config.name,
            "url": config.url
        })
        
    except Exception as e:
        logger.error(f"更新 MCP 配置失败: {str(e)}")
        return request.app.fail(msg=f"更新失败: {str(e)}")

async def delete_mcp_config(request: Request, config_id: int):
    """删除 MCP 配置"""
    try:
        from ...models.aitestrebort.project import aitestrebortMCPConfig
        
        config = await aitestrebortMCPConfig.get(
            id=config_id,
            user_id=request.state.user.id
        )
        
        await config.delete()
        
        return request.app.delete_success()
        
    except Exception as e:
        logger.error(f"删除 MCP 配置失败: {str(e)}")
        return request.app.fail(msg=f"删除失败: {str(e)}")


# API 密钥管理 - 占位实现
async def get_api_keys(request: Request):
    return request.app.get_success(data=[])

async def create_api_key(request: Request, key_data: dict):
    return request.app.post_success(data={})

async def update_api_key(request: Request, key_id: int, key_data: dict):
    return request.app.put_success(data={})

async def delete_api_key(request: Request, key_id: int):
    return request.app.delete_success()


# LLM 对话管理 - 基于原Django架构完整实现
async def get_conversations(request: Request):
    """
    获取用户的对话会话列表
    支持项目隔离，只返回指定项目的聊天会话
    """
    try:
        project_id = request.query_params.get('project_id')
        
        if not project_id:
            return request.app.fail(msg="project_id 参数是必需的")
        
        # 检查项目权限
        try:
            project = await aitestrebortProject.get(id=project_id)
        except DoesNotExist:
            return request.app.fail(msg="项目不存在")
        
        # 检查用户是否是项目成员
        is_member = await aitestrebortProjectMember.filter(
            project=project,
            user_id=request.state.user.id
        ).exists()
        
        if not is_member and not request.state.user.is_superuser:
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 获取该项目下的所有对话会话
        conversations = await aitestrebortConversation.filter(
            user_id=request.state.user.id,
            project=project
        ).prefetch_related('llm_config').order_by('-update_time').all()
        
        conversations_list = []
        for conv in conversations:
            llm_config_detail = None
            if conv.llm_config_id:
                try:
                    llm_config = await conv.llm_config
                    llm_config_detail = {
                        'id': llm_config.id,
                        'name': llm_config.name,
                        'provider': llm_config.provider,
                        'model_name': llm_config.model_name,
                    }
                except:
                    pass
            
            conversations_list.append({
                'id': conv.id,
                'title': conv.title,
                'llm_config_id': conv.llm_config_id,
                'llm_config_detail': llm_config_detail,
                'created_at': conv.create_time.isoformat() if conv.create_time else None,
                'updated_at': conv.update_time.isoformat() if conv.update_time else None,
            })
        
        return request.app.get_success(data={
            "project_id": project_id,
            "project_name": project.name,
            "conversations": conversations_list,
            "total": len(conversations_list)
        })
        
    except Exception as e:
        logger.error(f"Error in get_conversations: {str(e)}", exc_info=True)
        return request.app.error(msg=f"获取对话列表失败: {str(e)}")


async def create_conversation(request: Request, conversation_data: dict):
    """
    创建新的对话会话
    """
    try:
        project_id = conversation_data.get('project_id')
        title = conversation_data.get('title', '新对话')
        llm_config_id = conversation_data.get('llm_config_id')
        prompt_id = conversation_data.get('prompt_id')
        
        if not project_id:
            return request.app.fail(msg="project_id 是必需的")
        
        # 检查项目权限
        try:
            project = await aitestrebortProject.get(id=project_id)
        except DoesNotExist:
            return request.app.fail(msg="项目不存在")
        
        is_member = await aitestrebortProjectMember.filter(
            project=project,
            user_id=request.state.user.id
        ).exists()
        
        if not is_member and not request.state.user.is_superuser:
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 如果指定了 LLM 配置，验证其存在性并获取配置对象
        llm_config = None
        if llm_config_id:
            try:
                llm_config = await aitestrebortLLMConfig.get(
                    id=llm_config_id,
                    project_id=None,  # 全局配置
                    is_active=True
                )
            except DoesNotExist:
                return request.app.fail(msg="指定的 LLM 配置不存在或未激活")
        
        # 如果指定了提示词，验证其存在性并获取提示词对象
        prompt = None
        if prompt_id:
            try:
                from app.models.aitestrebort.project import aitestrebortPrompt
                prompt = await aitestrebortPrompt.get(
                    id=prompt_id,
                    user_id=request.state.user.id,
                    is_active=True
                )
            except DoesNotExist:
                return request.app.fail(msg="指定的提示词不存在或未激活")
        
        # 生成唯一的 session_id
        import uuid
        session_id = str(uuid.uuid4())
        
        # 创建对话
        conversation = await aitestrebortConversation.create(
            project=project,
            session_id=session_id,
            title=title,
            llm_config=llm_config,
            prompt=prompt,
            user_id=request.state.user.id
        )
        
        return request.app.post_success(data={
            'id': conversation.id,
            'title': conversation.title,
            'llm_config_id': conversation.llm_config_id if conversation.llm_config_id else None,
            'prompt_id': conversation.prompt_id if conversation.prompt_id else None,
            'project_id': project_id,
            'created_at': conversation.create_time.isoformat() if conversation.create_time else None,
            'updated_at': conversation.update_time.isoformat() if conversation.update_time else None,
        })
        
    except Exception as e:
        logger.error(f"Error in create_conversation: {str(e)}", exc_info=True)
        return request.app.error(msg=f"创建对话失败: {str(e)}")


async def update_conversation(request: Request, conversation_id: int, conversation_data: dict):
    """
    更新对话会话（主要是标题）
    """
    try:
        conversation = await aitestrebortConversation.get(
            id=conversation_id,
            user_id=request.state.user.id
        )
        
        # 更新字段
        if 'title' in conversation_data:
            conversation.title = conversation_data['title']
        
        if 'llm_config_id' in conversation_data:
            llm_config = None
            if conversation_data['llm_config_id']:
                try:
                    llm_config = await aitestrebortLLMConfig.get(
                        id=conversation_data['llm_config_id'],
                        project_id=None,
                        is_active=True
                    )
                except DoesNotExist:
                    return request.app.fail(msg="指定的 LLM 配置不存在或未激活")
            conversation.llm_config = llm_config
        
        await conversation.save()
        
        return request.app.put_success(data={
            'id': conversation.id,
            'title': conversation.title,
            'llm_config_id': conversation.llm_config_id,
            'updated_at': conversation.update_time.isoformat() if conversation.update_time else None,
        })
        
    except DoesNotExist:
        return request.app.fail(msg="对话不存在")
    except Exception as e:
        logger.error(f"Error in update_conversation: {str(e)}", exc_info=True)
        return request.app.error(msg=f"更新对话失败: {str(e)}")


async def delete_conversation(request: Request, conversation_id: int):
    """
    删除对话会话
    """
    try:
        conversation = await aitestrebortConversation.get(
            id=conversation_id,
            user_id=request.state.user.id
        )
        
        # 删除对话及其所有消息
        await aitestrebortMessage.filter(conversation=conversation).delete()
        await conversation.delete()
        
        return request.app.delete_success()
        
    except DoesNotExist:
        return request.app.fail(msg="对话不存在")
    except Exception as e:
        logger.error(f"Error in delete_conversation: {str(e)}", exc_info=True)
        return request.app.error(msg=f"删除对话失败: {str(e)}")


async def get_conversation_messages(request: Request, conversation_id: int):
    """
    获取对话的所有消息
    """
    try:
        conversation = await aitestrebortConversation.get(
            id=conversation_id,
            user_id=request.state.user.id
        )
        
        messages = await aitestrebortMessage.filter(
            conversation=conversation
        ).order_by('create_time').all()
        
        messages_list = []
        for msg in messages:
            messages_list.append({
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.create_time.isoformat() if msg.create_time else None,
            })
        
        return request.app.get_success(data={
            'conversation_id': conversation_id,
            'conversation_title': conversation.title,
            'messages': messages_list,
            'total': len(messages_list)
        })
        
    except DoesNotExist:
        return request.app.fail(msg="对话不存在")
    except Exception as e:
        logger.error(f"Error in get_conversation_messages: {str(e)}", exc_info=True)
        return request.app.error(msg=f"获取对话消息失败: {str(e)}")


async def send_message(request: Request, conversation_id: int, message_data: dict):
    """
    发送消息到对话
    使用LangChain进行对话
    """
    try:
        conversation = await aitestrebortConversation.get(
            id=conversation_id,
            user_id=request.state.user.id
        )
        
        content = message_data.get('content')
        if not content:
            return request.app.fail(msg="消息内容不能为空")
        
        # 保存用户消息
        user_message = await aitestrebortMessage.create(
            conversation=conversation,
            role='user',
            content=content,
            metadata={}
        )
        
        # 获取 LLM 配置
        llm_config = None
        if conversation.llm_config_id:
            try:
                llm_config = await aitestrebortLLMConfig.get(
                    id=conversation.llm_config_id,
                    is_active=True
                )
            except DoesNotExist:
                pass
        
        if not llm_config:
            # 使用默认配置
            llm_config = await aitestrebortLLMConfig.filter(
                project_id=None,
                is_default=True,
                is_active=True
            ).first()
        
        if not llm_config:
            return request.app.fail(msg="未找到可用的 LLM 配置")
        
        # 调用 LLM 生成回复
        try:
            from .ai_generator_real import create_llm_instance
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
            
            llm = create_llm_instance(llm_config, temperature=0.7)
            
            # 获取历史消息
            history_messages = await aitestrebortMessage.filter(
                conversation=conversation
            ).order_by('create_time').limit(20)  # 限制历史消息数量
            
            # 构建消息列表
            messages = []
            
            # 添加系统提示词（如果有）
            if llm_config.system_prompt:
                messages.append(SystemMessage(content=llm_config.system_prompt))
            
            # 添加历史消息
            for msg in history_messages:
                if msg.role == 'user':
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == 'assistant':
                    messages.append(AIMessage(content=msg.content))
            
            # 调用 LLM
            logger.info(f"Calling LLM for conversation {conversation_id}")
            response = llm.invoke(messages)
            
            # 保存 AI 回复
            ai_message = await aitestrebortMessage.create(
                conversation=conversation,
                role='assistant',
                content=response.content,
                metadata={}
            )
            
            # 更新对话的更新时间
            await conversation.save()
            
            return request.app.post_success(data={
                'user_message': {
                    'id': user_message.id,
                    'role': 'user',
                    'content': user_message.content,
                    'created_at': user_message.create_time.isoformat() if user_message.create_time else None,
                },
                'ai_message': {
                    'id': ai_message.id,
                    'role': 'assistant',
                    'content': ai_message.content,
                    'created_at': ai_message.create_time.isoformat() if ai_message.create_time else None,
                }
            })
            
        except Exception as e:
            logger.error(f"LLM invocation failed: {str(e)}", exc_info=True)
            return request.app.error(msg=f"AI 回复生成失败: {str(e)}")
        
    except DoesNotExist:
        return request.app.fail(msg="对话不存在")
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}", exc_info=True)
        return request.app.error(msg=f"发送消息失败: {str(e)}")



async def batch_delete_conversations(request: Request, conversation_ids: list = Body(..., embed=True)):
    """
    批量删除对话
    """
    try:
        if not conversation_ids:
            return request.app.fail(msg="conversation_ids 不能为空")
        
        deleted_count = 0
        failed_ids = []
        
        for conv_id in conversation_ids:
            try:
                conversation = await aitestrebortConversation.get(
                    id=conv_id,
                    user_id=request.state.user.id
                )
                
                # 删除消息
                await aitestrebortMessage.filter(conversation=conversation).delete()
                # 删除对话
                await conversation.delete()
                deleted_count += 1
                
            except DoesNotExist:
                failed_ids.append(conv_id)
                logger.warning(f"Conversation {conv_id} not found or no permission")
            except Exception as e:
                logger.error(f"Failed to delete conversation {conv_id}: {e}")
                failed_ids.append(conv_id)
        
        return request.app.success(
            msg=f"成功删除 {deleted_count} 个对话",
            data={
                'deleted_count': deleted_count,
                'failed_ids': failed_ids,
                'total': len(conversation_ids)
            }
        )
        
    except Exception as e:
        logger.error(f"Error in batch_delete_conversations: {str(e)}", exc_info=True)
        return request.app.error(msg=f"批量删除对话失败: {str(e)}")


async def clear_conversation_messages(request: Request, conversation_id: int):
    """
    清空对话消息
    """
    try:
        conversation = await aitestrebortConversation.get(
            id=conversation_id,
            user_id=request.state.user.id
        )
        
        deleted_count = await aitestrebortMessage.filter(
            conversation=conversation
        ).delete()
        
        return request.app.success(
            msg=f"已清空 {deleted_count} 条消息",
            data={'deleted_count': deleted_count}
        )
        
    except DoesNotExist:
        return request.app.fail(msg="对话不存在")
    except Exception as e:
        logger.error(f"Error in clear_conversation_messages: {str(e)}", exc_info=True)
        return request.app.error(msg=f"清空对话消息失败: {str(e)}")


async def export_conversation(request: Request, conversation_id: int):
    """
    导出对话
    支持多种格式：txt, json, markdown
    """
    try:
        format_type = request.query_params.get('format', 'txt')
        
        conversation = await aitestrebortConversation.get(
            id=conversation_id,
            user_id=request.state.user.id
        )
        
        messages = await aitestrebortMessage.filter(
            conversation=conversation
        ).order_by('create_time').all()
        
        if format_type == 'txt':
            from fastapi.responses import Response
            
            content = f"对话标题: {conversation.title}\n"
            content += f"创建时间: {conversation.create_time}\n"
            content += "=" * 50 + "\n\n"
            
            for msg in messages:
                role_label = "用户" if msg.role == "user" else "AI助手"
                content += f"[{role_label}] {msg.create_time}\n"
                content += f"{msg.content}\n\n"
            
            return Response(
                content=content,
                media_type="text/plain; charset=utf-8",
                headers={
                    "Content-Disposition": f"attachment; filename={conversation.title}.txt"
                }
            )
            
        elif format_type == 'json':
            from fastapi.responses import Response
            import json
            
            data = {
                'title': conversation.title,
                'created_at': conversation.create_time.isoformat() if conversation.create_time else None,
                'messages': [
                    {
                        'role': msg.role,
                        'content': msg.content,
                        'created_at': msg.create_time.isoformat() if msg.create_time else None
                    }
                    for msg in messages
                ]
            }
            
            return Response(
                content=json.dumps(data, ensure_ascii=False, indent=2),
                media_type="application/json; charset=utf-8",
                headers={
                    "Content-Disposition": f"attachment; filename={conversation.title}.json"
                }
            )
            
        elif format_type == 'markdown':
            from fastapi.responses import Response
            
            content = f"# {conversation.title}\n\n"
            content += f"**创建时间**: {conversation.create_time}\n\n"
            content += "---\n\n"
            
            for msg in messages:
                role_label = "👤 用户" if msg.role == "user" else "🤖 AI助手"
                content += f"## {role_label}\n\n"
                content += f"*{msg.create_time}*\n\n"
                content += f"{msg.content}\n\n"
                content += "---\n\n"
            
            return Response(
                content=content,
                media_type="text/markdown; charset=utf-8",
                headers={
                    "Content-Disposition": f"attachment; filename={conversation.title}.md"
                }
            )
        else:
            return request.app.fail(msg=f"不支持的导出格式: {format_type}")
        
    except DoesNotExist:
        return request.app.fail(msg="对话不存在")
    except Exception as e:
        logger.error(f"Error in export_conversation: {str(e)}", exc_info=True)
        return request.app.error(msg=f"导出对话失败: {str(e)}")
