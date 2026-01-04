"""
上下文压缩模块
用于管理长对话的上下文，防止超出Token限制
"""
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

logger = logging.getLogger(__name__)


@dataclass
class CompressionSettings:
    """上下文压缩配置"""
    max_context_tokens: int = 128000  # 最大上下文Token数
    trigger_ratio: float = 0.6  # 触发压缩的比例（60%时开始压缩）
    preserve_recent_messages: int = 8  # 保留最近的消息数量
    summary_max_tokens: int = 2000  # 摘要的最大Token数


class ConversationCompressor:
    """
    对话压缩器
    当对话历史接近Token限制时，自动压缩旧消息为摘要
    """
    
    def __init__(self, settings: CompressionSettings, llm=None):
        """
        初始化压缩器
        
        Args:
            settings: 压缩配置
            llm: LLM实例，用于生成摘要
        """
        self.settings = settings
        self.llm = llm
        self._token_counter = None
    
    def estimate_tokens(self, messages: List[BaseMessage]) -> int:
        """
        估算消息列表的Token数量
        使用简单的字符数估算：中文约1.5字符/token，英文约4字符/token
        
        Args:
            messages: 消息列表
            
        Returns:
            估算的Token数量
        """
        total_chars = 0
        for msg in messages:
            content = msg.content if hasattr(msg, 'content') else str(msg)
            total_chars += len(content)
        
        # 简单估算：平均2字符/token
        estimated_tokens = total_chars // 2
        
        logger.debug(f"Estimated tokens: {estimated_tokens} (from {total_chars} chars)")
        return estimated_tokens
    
    def should_compress(self, messages: List[BaseMessage]) -> bool:
        """
        判断是否需要压缩
        
        Args:
            messages: 消息列表
            
        Returns:
            是否需要压缩
        """
        current_tokens = self.estimate_tokens(messages)
        threshold = self.settings.max_context_tokens * self.settings.trigger_ratio
        
        should_compress = current_tokens > threshold
        
        if should_compress:
            logger.info(
                f"Context compression triggered: {current_tokens} tokens "
                f"> {threshold} threshold ({self.settings.trigger_ratio*100}%)"
            )
        
        return should_compress
    
    async def compress_messages(
        self,
        messages: List[BaseMessage],
        system_message: Optional[SystemMessage] = None
    ) -> List[BaseMessage]:
        """
        压缩消息列表
        保留系统消息和最近的N条消息，将旧消息压缩为摘要
        
        Args:
            messages: 原始消息列表
            system_message: 系统消息（可选）
            
        Returns:
            压缩后的消息列表
        """
        if not self.should_compress(messages):
            return messages
        
        # 分离系统消息和对话消息
        conversation_messages = [
            msg for msg in messages 
            if not isinstance(msg, SystemMessage)
        ]
        
        if len(conversation_messages) <= self.settings.preserve_recent_messages:
            logger.info("Not enough messages to compress")
            return messages
        
        # 计算需要压缩的消息数量
        compress_count = len(conversation_messages) - self.settings.preserve_recent_messages
        messages_to_compress = conversation_messages[:compress_count]
        recent_messages = conversation_messages[compress_count:]
        
        logger.info(
            f"Compressing {compress_count} messages, "
            f"preserving {len(recent_messages)} recent messages"
        )
        
        # 生成摘要
        summary = await self._generate_summary(messages_to_compress)
        
        # 构建压缩后的消息列表
        compressed_messages = []
        
        # 添加系统消息
        if system_message:
            compressed_messages.append(system_message)
        
        # 添加摘要消息
        summary_message = AIMessage(
            content=f"[历史对话摘要]\n{summary}",
            additional_kwargs={"compressed": True}
        )
        compressed_messages.append(summary_message)
        
        # 添加最近的消息
        compressed_messages.extend(recent_messages)
        
        # 验证压缩效果
        original_tokens = self.estimate_tokens(messages)
        compressed_tokens = self.estimate_tokens(compressed_messages)
        compression_ratio = (1 - compressed_tokens / original_tokens) * 100
        
        logger.info(
            f"Compression complete: {original_tokens} -> {compressed_tokens} tokens "
            f"({compression_ratio:.1f}% reduction)"
        )
        
        return compressed_messages
    
    async def _generate_summary(self, messages: List[BaseMessage]) -> str:
        """
        使用LLM生成消息摘要
        
        Args:
            messages: 需要摘要的消息列表
            
        Returns:
            摘要文本
        """
        if not self.llm:
            # 如果没有LLM，使用简单的文本截断
            return self._simple_summary(messages)
        
        try:
            # 构建摘要提示
            content_text = self._format_messages_for_summary(messages)
            
            summary_prompt = [
                SystemMessage(content="你是一个对话摘要助手，请简洁地总结对话的关键信息。"),
                HumanMessage(content=f"""请总结以下对话的关键内容：

{content_text}

要求：
1. 保留重要的事实和决策
2. 简洁明了，控制在200字以内
3. 使用第三人称叙述
4. 突出对话的主要目标和结果

摘要：""")
            ]
            
            # 调用LLM生成摘要
            response = await self.llm.ainvoke(summary_prompt)
            summary = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"Generated AI summary: {len(summary)} chars")
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate AI summary: {e}", exc_info=True)
            return self._simple_summary(messages)
    
    def _format_messages_for_summary(self, messages: List[BaseMessage]) -> str:
        """
        格式化消息用于摘要
        
        Args:
            messages: 消息列表
            
        Returns:
            格式化的文本
        """
        formatted = []
        for msg in messages:
            role = "用户" if isinstance(msg, HumanMessage) else "助手"
            content = msg.content if hasattr(msg, 'content') else str(msg)
            # 限制每条消息的长度
            content = content[:200] + "..." if len(content) > 200 else content
            formatted.append(f"{role}: {content}")
        
        return "\n".join(formatted)
    
    def _simple_summary(self, messages: List[BaseMessage]) -> str:
        """
        简单的文本摘要（不使用LLM）
        
        Args:
            messages: 消息列表
            
        Returns:
            摘要文本
        """
        summary_parts = []
        
        # 统计消息数量
        user_count = sum(1 for msg in messages if isinstance(msg, HumanMessage))
        ai_count = sum(1 for msg in messages if isinstance(msg, AIMessage))
        
        summary_parts.append(
            f"历史对话包含 {user_count} 条用户消息和 {ai_count} 条AI回复。"
        )
        
        # 提取前几条和后几条消息的关键内容
        if len(messages) > 0:
            first_msg = messages[0]
            first_content = first_msg.content if hasattr(first_msg, 'content') else str(first_msg)
            summary_parts.append(f"对话开始于：{first_content[:100]}...")
        
        if len(messages) > 1:
            last_msg = messages[-1]
            last_content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
            summary_parts.append(f"最近讨论：{last_content[:100]}...")
        
        return "\n".join(summary_parts)


def create_compressor(
    llm=None,
    max_context_tokens: int = 128000,
    trigger_ratio: float = 0.6,
    preserve_recent_messages: int = 8
) -> ConversationCompressor:
    """
    创建对话压缩器的工厂函数
    
    Args:
        llm: LLM实例
        max_context_tokens: 最大上下文Token数
        trigger_ratio: 触发压缩的比例
        preserve_recent_messages: 保留最近的消息数量
        
    Returns:
        ConversationCompressor实例
    """
    settings = CompressionSettings(
        max_context_tokens=max_context_tokens,
        trigger_ratio=trigger_ratio,
        preserve_recent_messages=preserve_recent_messages
    )
    
    return ConversationCompressor(settings, llm)
