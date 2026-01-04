"""
上下文管理器
管理AI对话的上下文，包括压缩、存储和检索
"""
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class ContextMessage:
    """上下文消息"""
    role: str  # system, user, assistant
    content: str
    timestamp: datetime
    token_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextMessage':
        """从字典创建"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class ContextSession:
    """上下文会话"""
    session_id: str
    messages: List[ContextMessage]
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def add_message(self, message: ContextMessage):
        """添加消息"""
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_total_tokens(self) -> int:
        """获取总token数"""
        return sum(msg.token_count or 0 for msg in self.messages)
    
    def get_recent_messages(self, count: int) -> List[ContextMessage]:
        """获取最近的消息"""
        return self.messages[-count:] if count > 0 else []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'session_id': self.session_id,
            'messages': [msg.to_dict() for msg in self.messages],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextSession':
        """从字典创建"""
        messages = [ContextMessage.from_dict(msg) for msg in data['messages']]
        return cls(
            session_id=data['session_id'],
            messages=messages,
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            metadata=data.get('metadata')
        )


class ContextManager:
    """上下文管理器"""
    
    def __init__(self, max_context_tokens: int = 8000, compression_threshold: float = 0.8):
        self.max_context_tokens = max_context_tokens
        self.compression_threshold = compression_threshold
        self.sessions: Dict[str, ContextSession] = {}
        self.llm_service = None  # 延迟初始化
    
    async def _get_llm_service(self):
        """获取LLM服务"""
        if self.llm_service is None:
            from .llm_service import get_llm_service
            self.llm_service = await get_llm_service()
        return self.llm_service
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """创建新会话"""
        if session_id is None:
            session_id = self._generate_session_id()
        
        session = ContextSession(
            session_id=session_id,
            messages=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created context session: {session_id}")
        return session_id
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        timestamp = datetime.now().isoformat()
        hash_obj = hashlib.md5(timestamp.encode())
        return hash_obj.hexdigest()[:16]
    
    def get_session(self, session_id: str) -> Optional[ContextSession]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        token_count: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """添加消息到会话"""
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return False
        
        message = ContextMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            token_count=token_count,
            metadata=metadata
        )
        
        session.add_message(message)
        logger.debug(f"Added message to session {session_id}: {role}")
        return True
    
    async def get_context_for_llm(
        self,
        session_id: str,
        max_tokens: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """获取用于LLM的上下文"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        max_tokens = max_tokens or self.max_context_tokens
        
        # 检查是否需要压缩
        total_tokens = session.get_total_tokens()
        if total_tokens > max_tokens * self.compression_threshold:
            await self._compress_context(session_id, max_tokens)
            session = self.get_session(session_id)  # 重新获取压缩后的会话
        
        # 转换为LLM格式
        llm_messages = []
        for message in session.messages:
            llm_messages.append({
                "role": message.role,
                "content": message.content
            })
        
        return llm_messages
    
    async def _compress_context(self, session_id: str, max_tokens: int):
        """压缩上下文"""
        session = self.get_session(session_id)
        if not session:
            return
        
        try:
            llm_service = await self._get_llm_service()
            
            # 保留系统消息和最近的消息
            system_messages = [msg for msg in session.messages if msg.role == "system"]
            recent_messages = session.messages[-3:]  # 保留最近3条消息
            
            # 需要压缩的消息
            to_compress = session.messages[len(system_messages):-3]
            
            if not to_compress:
                return
            
            # 生成压缩摘要
            compress_content = []
            for msg in to_compress:
                compress_content.append(f"{msg.role}: {msg.content}")
            
            compress_text = "\n".join(compress_content)
            
            summary = await llm_service.generate_text(
                f"""请将以下对话历史压缩为简洁的摘要，保留关键信息和重要结论：

{compress_text}

请用2-3句话总结对话的核心内容。""",
                temperature=0.3
            )
            
            # 创建压缩消息
            compressed_message = ContextMessage(
                role="assistant",
                content=f"[对话摘要] {summary}",
                timestamp=datetime.now(),
                token_count=len(summary) // 4,  # 粗略估算token数
                metadata={"compressed": True, "original_count": len(to_compress)}
            )
            
            # 重建消息列表
            new_messages = system_messages + [compressed_message] + recent_messages
            session.messages = new_messages
            session.updated_at = datetime.now()
            
            logger.info(f"Compressed context for session {session_id}: {len(to_compress)} -> 1 message")
            
        except Exception as e:
            logger.error(f"Context compression failed for session {session_id}: {e}")
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话摘要"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        return {
            "session_id": session_id,
            "message_count": len(session.messages),
            "total_tokens": session.get_total_tokens(),
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "duration": (session.updated_at - session.created_at).total_seconds(),
            "metadata": session.metadata
        }
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """列出所有会话"""
        summaries = []
        for session_id in self.sessions:
            summary = self.get_session_summary(session_id)
            if summary:
                summaries.append(summary)
        
        # 按更新时间排序
        summaries.sort(key=lambda x: x["updated_at"], reverse=True)
        return summaries
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted context session: {session_id}")
            return True
        return False
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """清理旧会话"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        to_delete = []
        
        for session_id, session in self.sessions.items():
            if session.updated_at < cutoff_time:
                to_delete.append(session_id)
        
        for session_id in to_delete:
            self.delete_session(session_id)
        
        if to_delete:
            logger.info(f"Cleaned up {len(to_delete)} old sessions")
    
    def export_session(self, session_id: str) -> Optional[str]:
        """导出会话为JSON"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        return json.dumps(session.to_dict(), ensure_ascii=False, indent=2)
    
    def import_session(self, session_data: str) -> Optional[str]:
        """从JSON导入会话"""
        try:
            data = json.loads(session_data)
            session = ContextSession.from_dict(data)
            self.sessions[session.session_id] = session
            logger.info(f"Imported context session: {session.session_id}")
            return session.session_id
        except Exception as e:
            logger.error(f"Failed to import session: {e}")
            return None
    
    def get_context_statistics(self) -> Dict[str, Any]:
        """获取上下文统计信息"""
        total_sessions = len(self.sessions)
        total_messages = sum(len(session.messages) for session in self.sessions.values())
        total_tokens = sum(session.get_total_tokens() for session in self.sessions.values())
        
        # 计算平均值
        avg_messages_per_session = total_messages / total_sessions if total_sessions > 0 else 0
        avg_tokens_per_session = total_tokens / total_sessions if total_sessions > 0 else 0
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "total_tokens": total_tokens,
            "avg_messages_per_session": round(avg_messages_per_session, 2),
            "avg_tokens_per_session": round(avg_tokens_per_session, 2),
            "max_context_tokens": self.max_context_tokens,
            "compression_threshold": self.compression_threshold
        }


# 全局上下文管理器实例
_context_manager = None


def get_context_manager() -> ContextManager:
    """获取上下文管理器实例"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager


# 便捷函数
def create_context_session(session_id: Optional[str] = None) -> str:
    """创建上下文会话的便捷函数"""
    manager = get_context_manager()
    return manager.create_session(session_id)


def add_context_message(
    session_id: str,
    role: str,
    content: str,
    token_count: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """添加上下文消息的便捷函数"""
    manager = get_context_manager()
    return manager.add_message(session_id, role, content, token_count, metadata)


async def get_llm_context(session_id: str, max_tokens: Optional[int] = None) -> List[Dict[str, str]]:
    """获取LLM上下文的便捷函数"""
    manager = get_context_manager()
    return await manager.get_context_for_llm(session_id, max_tokens)