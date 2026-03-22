"""
aitestrebort WebSocket 对话服务
"""
import logging
import json
import asyncio
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from tortoise.exceptions import DoesNotExist

from app.models.aitestrebort.project import (
    aitestrebortConversation,
    aitestrebortMessage,
    aitestrebortLLMConfig,
    aitestrebortProject,
    aitestrebortProjectMember,
    aitestrebortPrompt
)

# 导入对话管理服务
from .conversation_manager import (
    get_or_create_conversation,
    validate_conversation_access,
    save_message,
    load_conversation_history,
    get_conversation_llm_config,
    get_conversation_prompt
)

# 导入上下文压缩和checkpointer
from .context_compression import create_compressor
from .checkpointer import get_async_checkpointer

logger = logging.getLogger(__name__)


class ConversationWebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 存储活跃的WebSocket连接
        self.active_connections: Dict[int, WebSocket] = {}
        # 存储用户ID到连接的映射
        self.user_connections: Dict[int, Set[int]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int, conversation_id: int):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections[conversation_id] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(conversation_id)
        
        logger.info(f"WebSocket connected: user_id={user_id}, conversation_id={conversation_id}")
    
    def disconnect(self, user_id: int, conversation_id: int):
        """断开WebSocket连接"""
        if conversation_id in self.active_connections:
            del self.active_connections[conversation_id]
        
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(conversation_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(f"WebSocket disconnected: user_id={user_id}, conversation_id={conversation_id}")
    
    async def send_message(self, conversation_id: int, message: str):
        """发送消息到指定对话"""
        if conversation_id in self.active_connections:
            try:
                await self.active_connections[conversation_id].send_text(message)
            except Exception as e:
                logger.error(f"Failed to send message to conversation {conversation_id}: {e}")
                # 移除失效的连接
                del self.active_connections[conversation_id]


# 全局WebSocket管理器实例
websocket_manager = ConversationWebSocketManager()


async def handle_websocket_conversation(websocket: WebSocket, user_id: int, conversation_id: int, project_id: int = 1):
    """
    处理WebSocket对话连接
    """
    await websocket_manager.connect(websocket, user_id, conversation_id)
    
    conversation = None
    try:
        # 获取或创建对话记录
        conversation = await get_or_create_conversation(
            conversation_id=conversation_id,
            project_id=project_id,
            user_id=user_id,
            title="WebSocket对话"
        )
        
        if not conversation:
            await websocket.send_text(json.dumps({
                'type': 'error',
                'message': '无法创建或获取对话记录'
            }))
            return
        
        # 验证访问权限
        has_access = await validate_conversation_access(conversation, user_id)
        if not has_access:
            await websocket.send_text(json.dumps({
                'type': 'error',
                'message': '无权限访问此对话'
            }))
            return
        
        # 发送连接成功消息
        await websocket.send_text(json.dumps({
            'type': 'connected',
            'message': '连接成功',
            'conversation_id': conversation.id
        }))
        
        # 监听客户端消息
        while True:
            # 接收用户消息 - 直接接收文本
            user_message = await websocket.receive_text()
            
            if not user_message.strip():
                continue
            
            # 保存用户消息
            await save_message(conversation, 'user', user_message)
            
            # 处理AI回复
            await process_ai_response(websocket, conversation, user_message, user_id)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected normally: conversation_id={conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_text(json.dumps({
                'type': 'error',
                'message': f'服务器错误: {str(e)}'
            }))
        except:
            pass
    finally:
        websocket_manager.disconnect(user_id, conversation_id)


async def process_ai_response(websocket: WebSocket, conversation: aitestrebortConversation, user_message: str, user_id: int):
    """
    处理AI回复，实现流式响应
    """
    try:
        # 获取LLM配置
        llm_config = await get_conversation_llm_config(conversation)
        
        if not llm_config:
            await websocket.send_text(json.dumps({
                'type': 'error',
                'message': '未找到可用的 LLM 配置'
            }))
            return
        
        # 创建LLM实例
        try:
            from .ai_generator_real import create_llm_instance
            llm = create_llm_instance(llm_config, temperature=0.7)
        except Exception as e:
            logger.error(f"Failed to create LLM instance: {e}", exc_info=True)
            await websocket.send_text(json.dumps({
                'type': 'error',
                'message': f'LLM 初始化失败: {str(e)}'
            }))
            return
        
        # 加载历史消息
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        messages = []
        
        # 添加系统提示词
        prompt_content = await get_conversation_prompt(conversation)
        if prompt_content:
            messages.append(SystemMessage(content=prompt_content))
        
        # 加载历史对话消息
        history_messages = await load_conversation_history(conversation, limit=20)
        
        for msg in history_messages:
            if msg.role == 'user':
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == 'assistant':
                messages.append(AIMessage(content=msg.content))
        
        # 添加当前用户消息
        messages.append(HumanMessage(content=user_message))
        
        # 上下文压缩检查
        compressor = create_compressor(
            llm=llm,
            max_context_tokens=llm_config.context_limit,
            trigger_ratio=0.6,
            preserve_recent_messages=8
        )
        
        if compressor.should_compress(messages):
            logger.info("Compressing conversation context...")
            system_message = messages[0] if messages and isinstance(messages[0], SystemMessage) else None
            messages = await compressor.compress_messages(messages, system_message)
        
        # 流式调用LLM并实时发送响应
        ai_content = ""
        try:
            async for chunk in llm.astream(messages):
                if hasattr(chunk, 'content') and chunk.content:
                    content_chunk = chunk.content
                    ai_content += content_chunk
                    
                    # 直接发送内容块
                    await websocket.send_text(content_chunk)
                    
                    # 小延迟确保流式效果
                    await asyncio.sleep(0.01)
            
        except Exception as e:
            logger.error(f"LLM streaming failed: {e}", exc_info=True)
            await websocket.send_text(json.dumps({
                'type': 'error',
                'message': f'AI 回复生成失败: {str(e)}'
            }))
            return
        
        # 保存AI回复到数据库
        await save_message(conversation, 'assistant', ai_content)
        
        logger.info(f"AI response completed for conversation {conversation.id}")
        
    except Exception as e:
        logger.error(f"Error processing AI response: {e}", exc_info=True)
        try:
            await websocket.send_text(json.dumps({
                'type': 'error',
                'message': f'处理AI回复时发生错误: {str(e)}'
            }))
        except:
            pass