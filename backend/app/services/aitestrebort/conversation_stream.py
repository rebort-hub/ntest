"""
aitestrebort 对话流式响应服务
集成上下文压缩和LangGraph checkpointer
"""
import logging
import json
import asyncio
from typing import AsyncGenerator
from fastapi import Request
from fastapi.responses import StreamingResponse
from tortoise.exceptions import DoesNotExist

from app.models.aitestrebort.project import (
    aitestrebortConversation,
    aitestrebortMessage,
    aitestrebortLLMConfig,
    aitestrebortProject,
    aitestrebortProjectMember,
    aitestrebortPrompt
)

# 导入上下文压缩和checkpointer
from .context_compression import create_compressor
from .checkpointer import get_async_checkpointer

logger = logging.getLogger(__name__)


def create_sse_data(data_dict: dict) -> str:
    """
    创建SSE格式的数据，确保中文字符正确编码
    """
    json_str = json.dumps(data_dict, ensure_ascii=False)
    return f"data: {json_str}\n\n"


async def send_message_stream(request: Request, conversation_id: int, message_data: dict):
    """
    流式发送消息并获取AI回复
    使用SSE (Server-Sent Events) 实现实时流式响应
    """
    
    async def generate() -> AsyncGenerator[str, None]:
        """SSE事件生成器"""
        try:
            # 获取用户信息
            if not hasattr(request.state, 'user') or not request.state.user:
                yield create_sse_data({
                    'type': 'error',
                    'message': '用户未登录，请重新登录'
                })
                return
            
            user_id = request.state.user.id
            
            # 1. 验证对话存在性和权限
            try:
                conversation = await aitestrebortConversation.get(
                    id=conversation_id,
                    user_id=user_id
                )
            except DoesNotExist:
                yield create_sse_data({
                    'type': 'error',
                    'message': '对话不存在或无权限访问'
                })
                return
            
            # 2. 获取消息内容
            content = message_data.get('content', '').strip()
            if not content:
                yield create_sse_data({
                    'type': 'error',
                    'message': '消息内容不能为空'
                })
                return
            
            # 3. 保存用户消息
            user_message = await aitestrebortMessage.create(
                conversation=conversation,
                role='user',
                content=content
            )
            
            # 发送用户消息确认
            yield create_sse_data({
                'type': 'user_message',
                'message_id': user_message.id,
                'content': content
            })
            
            # 立即发送"开始处理"信号，让前端知道后端已经开始工作
            yield create_sse_data({
                'type': 'processing',
                'message': '正在准备回复...'
            })
            
            # 4. 获取 LLM 配置
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
                yield create_sse_data({
                    'type': 'error',
                    'message': '未找到可用的 LLM 配置'
                })
                return
            
            # 5. 创建 LLM 实例
            try:
                from .ai_generator_real import create_llm_instance
                llm = create_llm_instance(llm_config, temperature=0.7)
            except Exception as e:
                logger.error(f"Failed to create LLM instance: {e}", exc_info=True)
                yield create_sse_data({
                    'type': 'error',
                    'message': f'LLM 初始化失败: {str(e)}'
                })
                return
            
            # 加载历史消息
            use_checkpointer = message_data.get('use_checkpointer', False)  # 默认禁用checkpointer
            
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
            
            messages = []
            
            # 添加系统提示词
            system_prompt = None
            system_message = None
            
            # 优先使用对话关联的提示词
            if conversation.prompt_id:
                try:
                    prompt = await aitestrebortPrompt.get(
                        id=conversation.prompt_id,
                        is_active=True
                    )
                    system_prompt = prompt.content
                except DoesNotExist:
                    pass
            
            # 如果没有关联提示词，使用 LLM 配置的系统提示词
            if not system_prompt and llm_config.system_prompt:
                system_prompt = llm_config.system_prompt
            
            if system_prompt:
                system_message = SystemMessage(content=system_prompt)
                messages.append(system_message)
            
            # 加载历史消息
            if use_checkpointer:
                # 使用checkpointer加载历史
                thread_id = f"user_{user_id}_conv_{conversation_id}"
                
                try:
                    async with get_async_checkpointer() as checkpointer:
                        # 尝试加载历史状态
                        config = {"configurable": {"thread_id": thread_id}}
                        
                        try:
                            checkpoint_tuple = await checkpointer.aget(config)
                            
                            if checkpoint_tuple:
                                checkpoint_dict = checkpoint_tuple[0] if isinstance(checkpoint_tuple, tuple) else checkpoint_tuple
                                if checkpoint_dict and isinstance(checkpoint_dict, dict):
                                    channel_values = checkpoint_dict.get("channel_values", {})
                                    history_messages = channel_values.get("messages", [])
                                    
                                    if history_messages:
                                        logger.info(f"Loaded {len(history_messages)} messages from checkpointer")
                                        messages.extend(history_messages)
                                    else:
                                        logger.info("No history in checkpointer, loading from database")
                                        await _load_messages_from_db(conversation, messages)
                                else:
                                    await _load_messages_from_db(conversation, messages)
                            else:
                                logger.info("No checkpoint found, loading from database")
                                await _load_messages_from_db(conversation, messages)
                        except AttributeError as e:
                            # 处理 'Connection' object has no attribute 'is_alive' 错误
                            logger.warning(f"Checkpointer attribute error: {e}, loading from database")
                            await _load_messages_from_db(conversation, messages)
                            
                except Exception as e:
                    logger.warning(f"Failed to load from checkpointer: {e}, falling back to database")
                    await _load_messages_from_db(conversation, messages)
            else:
                # 直接从数据库加载
                await _load_messages_from_db(conversation, messages)
            
            # 7. 上下文压缩检查
            compressor = create_compressor(
                llm=llm,
                max_context_tokens=llm_config.context_limit,
                trigger_ratio=0.6,
                preserve_recent_messages=8
            )
            
            # 估算当前token数
            current_tokens = compressor.estimate_tokens(messages)
            
            # 发送上下文信息
            yield create_sse_data({
                'type': 'context_info',
                'current_tokens': current_tokens,
                'max_tokens': llm_config.context_limit,
                'usage_ratio': round(current_tokens / llm_config.context_limit, 2)
            })
            
            # 如果需要压缩
            if compressor.should_compress(messages):
                logger.info("Compressing conversation context...")
                yield create_sse_data({
                    'type': 'context_compression',
                    'message': '对话历史较长，正在压缩上下文...'
                })
                
                messages = await compressor.compress_messages(messages, system_message)
                
                compressed_tokens = compressor.estimate_tokens(messages)
                yield create_sse_data({
                    'type': 'context_compressed',
                    'original_tokens': current_tokens,
                    'compressed_tokens': compressed_tokens,
                    'message': f'上下文已压缩：{current_tokens} -> {compressed_tokens} tokens'
                })
            
            # 8. 发送开始信号
            yield create_sse_data({
                'type': 'start',
                'conversation_id': conversation_id,
                'llm_config': llm_config.name
            })
            
            # 9. 流式调用 LLM
            ai_content = ""
            try:
                async for chunk in llm.astream(messages):
                    if hasattr(chunk, 'content') and chunk.content:
                        content_chunk = chunk.content
                        ai_content += content_chunk
                        
                        # 发送内容块
                        yield create_sse_data({
                            'type': 'content',
                            'content': content_chunk
                        })
                        
                        # 添加小延迟以确保流式传输效果
                        await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"LLM streaming failed: {e}", exc_info=True)
                yield create_sse_data({
                    'type': 'error',
                    'message': f'AI 回复生成失败: {str(e)}'
                })
                return
            
            # 10. 保存 AI 回复到数据库
            ai_message = await aitestrebortMessage.create(
                conversation=conversation,
                role='assistant',
                content=ai_content
            )
            
            # 11. 保存到checkpointer（如果启用）
            if use_checkpointer:
                try:
                    thread_id = f"user_{user_id}_conv_{conversation_id}"
                    
                    # 添加新消息到messages列表
                    messages.append(HumanMessage(content=content))
                    messages.append(AIMessage(content=ai_content))
                    
                    async with get_async_checkpointer() as checkpointer:
                        # 保存状态
                        config = {"configurable": {"thread_id": thread_id}}
                        state = {"messages": messages}
                        
                        await checkpointer.aput(config, state, {})
                        logger.info(f"Saved conversation state to checkpointer: {thread_id}")
                        
                except Exception as e:
                    logger.error(f"Failed to save to checkpointer: {e}", exc_info=True)
            
            # 12. 更新对话的更新时间
            await conversation.save()
            
            # 13. 发送完成信号
            yield create_sse_data({
                'type': 'complete',
                'message_id': ai_message.id,
                'total_content': ai_content
            })
            
            # 14. 发送流结束标记
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Error in stream generator: {e}", exc_info=True)
            yield create_sse_data({
                'type': 'error',
                'message': f'流式响应错误: {str(e)}'
            })
    
    # 返回 StreamingResponse
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
        }
    )


async def _load_messages_from_db(conversation, messages):
    """
    从数据库加载历史消息的辅助方法
    
    Args:
        conversation: 对话对象
        messages: 消息列表（会被修改）
    """
    from langchain_core.messages import HumanMessage, AIMessage
    
    history_messages = await aitestrebortMessage.filter(
        conversation=conversation
    ).order_by('create_time').limit(20)
    
    for msg in history_messages:
        if msg.role == 'user':
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == 'assistant':
            messages.append(AIMessage(content=msg.content))
