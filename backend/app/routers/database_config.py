"""
数据库配置管理API，提供数据库类型切换和配置管理功能
"""
import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.tools.db_compatibility import DatabaseCompatibility
from tortoise import Tortoise


router = APIRouter(prefix="/api/database", tags=["数据库配置"])


class DatabaseConfigModel(BaseModel):
    """数据库配置模型"""
    db_type: str  # mysql 或 postgresql
    host: str
    port: int
    user: str
    password: str
    database: str


class DatabaseStatusResponse(BaseModel):
    """数据库状态响应"""
    current_type: str
    is_connected: bool
    version: Optional[str] = None
    connection_info: Dict[str, Any]


@router.get("/status", response_model=DatabaseStatusResponse)
async def get_database_status():
    """获取当前数据库状态"""
    try:
        db_type = DatabaseCompatibility.get_db_type()
        
        # 检查数据库连接
        db = Tortoise.get_connection("default")
        is_connected = True
        
        # 获取数据库版本信息
        if DatabaseCompatibility.is_postgresql():
            result = await db.execute_query("SELECT version();")
            version = str(result[0][0]) if result else None
        else:
            result = await db.execute_query("SELECT VERSION();")
            version = str(result[0][0]) if result else None
        
        connection_info = {
            "host": os.environ.get('DB_HOST', 'localhost'),
            "port": os.environ.get('DB_PORT'),
            "database": os.environ.get('DB_NAME'),
            "user": os.environ.get('DB_USER')
        }
        
        return DatabaseStatusResponse(
            current_type=db_type,
            is_connected=is_connected,
            version=version,
            connection_info=connection_info
        )
        
    except Exception as e:
        return DatabaseStatusResponse(
            current_type=DatabaseCompatibility.get_db_type(),
            is_connected=False,
            connection_info={}
        )


@router.post("/test-connection")
async def test_database_connection(config: DatabaseConfigModel):
    """测试数据库连接"""
    try:
        # 构建测试配置
        if config.db_type.lower() == 'postgresql':
            test_config = {
                'connections': {
                    'test': {
                        'engine': 'tortoise.backends.asyncpg',
                        'credentials': {
                            'host': config.host,
                            'port': config.port,
                            'user': config.user,
                            'password': config.password,
                            'database': config.database,
                            'minsize': 1,
                            'maxsize': 1,
                        }
                    }
                },
                'apps': {
                    'test': {
                        'models': [],
                        "default_connection": "test",
                    }
                }
            }
        else:  # mysql
            test_config = {
                'connections': {
                    'test': {
                        'engine': 'tortoise.backends.mysql',
                        'credentials': {
                            'host': config.host,
                            'port': config.port,
                            'user': config.user,
                            'password': config.password,
                            'database': config.database,
                        }
                    }
                },
                'apps': {
                    'test': {
                        'models': [],
                        "default_connection": "test",
                    }
                }
            }
        
        # 测试连接
        await Tortoise.init(config=test_config)
        test_db = Tortoise.get_connection("test")
        await test_db.execute_query("SELECT 1;")
        await Tortoise.close_connections()
        
        return {"success": True, "message": "数据库连接测试成功"}
        
    except Exception as e:
        await Tortoise.close_connections()
        raise HTTPException(status_code=400, detail=f"数据库连接测试失败: {str(e)}")


@router.get("/compatibility-info")
async def get_compatibility_info():
    """获取数据库兼容性信息"""
    return {
        "current_type": DatabaseCompatibility.get_db_type(),
        "supported_types": ["mysql", "postgresql"],
        "features": {
            "mysql": {
                "json_support": True,
                "full_text_search": True,
                "window_functions": True,
                "cte_support": True
            },
            "postgresql": {
                "json_support": True,
                "jsonb_support": True,
                "full_text_search": True,
                "window_functions": True,
                "cte_support": True,
                "array_support": True
            }
        },
        "migration_notes": {
            "mysql_to_postgresql": [
                "LONGTEXT -> TEXT",
                "TINYINT(1) -> BOOLEAN", 
                "DATETIME -> TIMESTAMP",
                "反引号(`) -> 双引号(\")"
            ],
            "postgresql_to_mysql": [
                "TEXT -> LONGTEXT",
                "BOOLEAN -> TINYINT(1)",
                "TIMESTAMP -> DATETIME", 
                "双引号(\") -> 反引号(`)"
            ]
        }
    }


@router.post("/switch-type")
async def switch_database_type(db_type: str):
    """切换数据库类型（需要重启应用）"""
    if db_type.lower() not in ['mysql', 'postgresql']:
        raise HTTPException(status_code=400, detail="不支持的数据库类型")
    
    # 这里只是设置环境变量，实际切换需要重启应用
    os.environ['DB_TYPE'] = db_type.lower()
    
    return {
        "success": True,
        "message": f"数据库类型已设置为 {db_type}，请重启应用以生效",
        "restart_required": True
    }