"""
LangGraph Checkpointer 集成模块
提供统一的checkpointer工厂函数，支持SQLite持久化
"""
import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager, contextmanager
from typing import Optional, List
import aiosqlite
import sqlite3

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.checkpoint.sqlite import SqliteSaver

logger = logging.getLogger(__name__)

# 默认的checkpointer数据库路径
DEFAULT_CHECKPOINT_DB = "chat_history.sqlite"


def get_checkpoint_db_path() -> str:
    """
    获取checkpointer数据库路径
    优先使用环境变量，否则使用默认路径
    
    Returns:
        数据库文件路径
    """
    # 从环境变量获取
    db_path = os.getenv("CHECKPOINT_DB_PATH", DEFAULT_CHECKPOINT_DB)
    
    # 确保目录存在
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Using checkpoint database: {db_path}")
    return db_path


@asynccontextmanager
async def get_async_checkpointer():
    """
    异步上下文管理器：获取异步checkpointer实例
    
    使用方式：
        async with get_async_checkpointer() as checkpointer:
            # 使用checkpointer
            pass
    
    Yields:
        AsyncSqliteSaver实例
    """
    db_path = get_checkpoint_db_path()
    
    # 使用AsyncSqliteSaver.from_conn_string创建实例（它返回一个context manager）
    async with AsyncSqliteSaver.from_conn_string(db_path) as checkpointer:
        logger.debug(f"Async checkpointer initialized with {db_path}")
        yield checkpointer
        logger.debug("Async checkpointer connection closed")


@contextmanager
def get_sync_checkpointer():
    """
    同步上下文管理器：获取同步checkpointer实例
    
    使用方式：
        with get_sync_checkpointer() as checkpointer:
            # 使用checkpointer
            pass
    
    Yields:
        SqliteSaver实例
    """
    db_path = get_checkpoint_db_path()
    
    # 使用SqliteSaver.from_conn_string创建实例（它返回一个context manager）
    with SqliteSaver.from_conn_string(db_path) as checkpointer:
        logger.debug(f"Sync checkpointer initialized with {db_path}")
        yield checkpointer
        logger.debug("Sync checkpointer connection closed")


async def delete_checkpoints_by_thread_id(thread_id: str) -> int:
    """
    删除指定thread_id的所有checkpoint记录
    
    Args:
        thread_id: 线程ID
        
    Returns:
        删除的记录数
    """
    db_path = get_checkpoint_db_path()
    
    async with aiosqlite.connect(db_path) as conn:
        cursor = await conn.execute(
            "DELETE FROM checkpoints WHERE thread_id = ?",
            (thread_id,)
        )
        deleted_count = cursor.rowcount
        await conn.commit()
        
        logger.info(f"Deleted {deleted_count} checkpoints for thread_id: {thread_id}")
        return deleted_count


async def delete_checkpoints_batch(thread_ids: List[str]) -> int:
    """
    批量删除多个thread_id的checkpoint记录
    
    Args:
        thread_ids: 线程ID列表
        
    Returns:
        删除的记录数
    """
    if not thread_ids:
        return 0
    
    db_path = get_checkpoint_db_path()
    
    async with aiosqlite.connect(db_path) as conn:
        placeholders = ",".join("?" * len(thread_ids))
        cursor = await conn.execute(
            f"DELETE FROM checkpoints WHERE thread_id IN ({placeholders})",
            thread_ids
        )
        deleted_count = cursor.rowcount
        await conn.commit()
        
        logger.info(f"Batch deleted {deleted_count} checkpoints for {len(thread_ids)} thread_ids")
        return deleted_count


async def check_history_exists(thread_id: str) -> bool:
    """
    检查指定thread_id是否存在历史记录
    
    Args:
        thread_id: 线程ID
        
    Returns:
        是否存在历史记录
    """
    db_path = get_checkpoint_db_path()
    
    async with aiosqlite.connect(db_path) as conn:
        cursor = await conn.execute(
            "SELECT COUNT(*) FROM checkpoints WHERE thread_id = ?",
            (thread_id,)
        )
        row = await cursor.fetchone()
        count = row[0] if row else 0
        
        exists = count > 0
        logger.debug(f"Thread {thread_id} has {count} checkpoints (exists: {exists})")
        return exists


async def get_thread_ids_by_prefix(prefix: str) -> List[str]:
    """
    获取指定前缀的所有thread_id
    用于查询特定用户或项目的所有对话
    
    Args:
        prefix: thread_id前缀（如 "user_123_project_456"）
        
    Returns:
        thread_id列表
    """
    db_path = get_checkpoint_db_path()
    
    async with aiosqlite.connect(db_path) as conn:
        cursor = await conn.execute(
            "SELECT DISTINCT thread_id FROM checkpoints WHERE thread_id LIKE ?",
            (f"{prefix}%",)
        )
        rows = await cursor.fetchall()
        thread_ids = [row[0] for row in rows]
        
        logger.debug(f"Found {len(thread_ids)} thread_ids with prefix: {prefix}")
        return thread_ids


async def get_checkpoint_stats() -> dict:
    """
    获取checkpoint数据库的统计信息
    
    Returns:
        统计信息字典
    """
    db_path = get_checkpoint_db_path()
    
    async with aiosqlite.connect(db_path) as conn:
        # 总记录数
        cursor = await conn.execute("SELECT COUNT(*) FROM checkpoints")
        row = await cursor.fetchone()
        total_checkpoints = row[0] if row else 0
        
        # 唯一thread数
        cursor = await conn.execute("SELECT COUNT(DISTINCT thread_id) FROM checkpoints")
        row = await cursor.fetchone()
        unique_threads = row[0] if row else 0
        
        # 数据库文件大小
        db_file = Path(db_path)
        file_size = db_file.stat().st_size if db_file.exists() else 0
        
        stats = {
            "total_checkpoints": total_checkpoints,
            "unique_threads": unique_threads,
            "database_size_bytes": file_size,
            "database_size_mb": round(file_size / (1024 * 1024), 2),
            "database_path": db_path
        }
        
        logger.info(f"Checkpoint stats: {stats}")
        return stats


def cleanup_old_checkpoints(days: int = 30) -> int:
    """
    清理超过指定天数的旧checkpoint记录
    注意：这是同步函数，适合在定时任务中使用
    
    Args:
        days: 保留天数
        
    Returns:
        删除的记录数
    """
    db_path = get_checkpoint_db_path()
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            """
            DELETE FROM checkpoints 
            WHERE datetime(created_at) < datetime('now', '-' || ? || ' days')
            """,
            (days,)
        )
        deleted_count = cursor.rowcount
        conn.commit()
        
        logger.info(f"Cleaned up {deleted_count} checkpoints older than {days} days")
        return deleted_count
