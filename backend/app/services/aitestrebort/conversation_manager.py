"""
对话管理服务
"""
import logging
from typing import Optional, List, Dict, Any
from tortoise.exceptions import DoesNotExist

from app.models.aitestrebort.project import (
    aitestrebortConversation,
    aitestrebortMessage,
    aitestrebortLLMConfig,
    aitestrebortProject,
    aitestrebortProjectMember,
    aitestrebortPrompt
)

logger = logging.getLogger(__name__)


async def get_or_create_conversation(
    conversation_id: int,
    project_id: int,
    user_id: int,
    title: str = "新对话"
) -> Optional[aitestrebortConversation]:
    """
    获取或创建对话记录
    
    参数:
    - conversation_id: 对话ID
    - project_id: 项目ID
    - user_id: 用户ID
    - title: 对话标题（创建时使用）
    
    返回:
    - aitestrebortConversation: 对话记录，如果失败返回None
    """
    try:
        # 尝试获取现有对话
        conversation = await aitestrebortConversation.get(id=conversation_id)
        logger.info(f"Found existing conversation {conversation_id}")
        return conversation
    except DoesNotExist:
        # 对话不存在，尝试创建
        try:
            # 验证项目是否存在
            project = await aitestrebortProject.get(id=project_id)
            
            # 获取默认LLM配置
            llm_config = await aitestrebortLLMConfig.filter(
                project_id=None,
                is_default=True,
                is_active=True
            ).first()
            
            # 创建新对话
            import uuid
            session_id = f"ws-{uuid.uuid4().hex[:16]}"
            
            conversation = await aitestrebortConversation.create(
                project=project,
                session_id=session_id,
                title=title,
                llm_config=llm_config,
                user_id=user_id,
                is_active=True
            )
            
            logger.info(f"Created new conversation {conversation.id} for project {project_id}")
            return conversation
            
        except DoesNotExist:
            logger.error(f"Project {project_id} not found")
            return None
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}", exc_info=True)
            return None


async def validate_conversation_access(
    conversation: aitestrebortConversation,
    user_id: int
) -> bool:
    """
    验证用户是否有权限访问对话
    
    参数:
    - conversation: 对话记录
    - user_id: 用户ID
    
    返回:
    - bool: 是否有权限
    """
    try:
        # 检查用户是否是项目成员
        project = await aitestrebortProject.get(id=conversation.project_id)
        is_member = await aitestrebortProjectMember.filter(
            project=project,
            user_id=user_id
        ).exists()
        
        if not is_member:
            logger.warning(f"User {user_id} has no access to conversation {conversation.id}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to validate conversation access: {e}", exc_info=True)
        return False


async def save_message(
    conversation: aitestrebortConversation,
    role: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[aitestrebortMessage]:
    """
    保存消息到数据库
    
    参数:
    - conversation: 对话记录
    - role: 消息角色 (user/assistant/system)
    - content: 消息内容
    - metadata: 元数据
    
    返回:
    - aitestrebortMessage: 消息记录，如果失败返回None
    """
    try:
        message = await aitestrebortMessage.create(
            conversation=conversation,
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        # 更新对话时间
        await conversation.save()
        
        logger.debug(f"Saved {role} message to conversation {conversation.id}")
        return message
        
    except Exception as e:
        logger.error(f"Failed to save message: {e}", exc_info=True)
        return None


async def load_conversation_history(
    conversation: aitestrebortConversation,
    limit: int = 20
) -> List[aitestrebortMessage]:
    """
    加载对话历史消息
    
    参数:
    - conversation: 对话记录
    - limit: 最大消息数量
    
    返回:
    - List[aitestrebortMessage]: 消息列表
    """
    try:
        messages = await aitestrebortMessage.filter(
            conversation=conversation
        ).order_by('create_time').limit(limit)
        
        logger.debug(f"Loaded {len(messages)} messages for conversation {conversation.id}")
        return messages
        
    except Exception as e:
        logger.error(f"Failed to load conversation history: {e}", exc_info=True)
        return []


async def get_conversation_llm_config(
    conversation: aitestrebortConversation
) -> Optional[aitestrebortLLMConfig]:
    """
    获取对话的LLM配置
    
    参数:
    - conversation: 对话记录
    
    返回:
    - aitestrebortLLMConfig: LLM配置，如果失败返回None
    """
    try:
        # 优先使用对话指定的配置
        if conversation.llm_config_id:
            try:
                llm_config = await aitestrebortLLMConfig.get(
                    id=conversation.llm_config_id,
                    is_active=True
                )
                return llm_config
            except DoesNotExist:
                pass
        
        # 使用默认配置
        llm_config = await aitestrebortLLMConfig.filter(
            project_id=None,
            is_default=True,
            is_active=True
        ).first()
        
        return llm_config
        
    except Exception as e:
        logger.error(f"Failed to get LLM config: {e}", exc_info=True)
        return None


async def get_conversation_prompt(
    conversation: aitestrebortConversation
) -> Optional[str]:
    """
    获取对话的系统提示词
    
    参数:
    - conversation: 对话记录
    
    返回:
    - str: 提示词内容，如果没有返回None
    """
    try:
        if conversation.prompt_id:
            prompt = await aitestrebortPrompt.get(id=conversation.prompt_id)
            return prompt.content
        return None
    except DoesNotExist:
        return None
    except Exception as e:
        logger.error(f"Failed to get conversation prompt: {e}", exc_info=True)
        return None
