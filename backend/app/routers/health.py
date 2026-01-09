"""
健康检查路由
用于Docker健康检查和服务监控
"""
from fastapi import APIRouter, HTTPException
from tortoise import Tortoise
from app.tools.db_compatibility import DatabaseCompatibility
from config import tortoise_orm_conf

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        # 检查数据库连接
        db = Tortoise.get_connection("default")
        await db.execute_query("SELECT 1")
        
        return {
            "status": "healthy",
            "database": {
                "type": DatabaseCompatibility.get_db_type(),
                "connected": True
            },
            "message": "服务运行正常"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": {
                    "type": DatabaseCompatibility.get_db_type(),
                    "connected": False,
                    "error": str(e)
                },
                "message": "服务异常"
            }
        )


@router.get("/ready")
async def readiness_check():
    """就绪检查端点"""
    try:
        # 检查数据库是否已初始化
        from app.models.system.user import User
        user_count = await User.all().count()
        
        return {
            "status": "ready",
            "database": {
                "type": DatabaseCompatibility.get_db_type(),
                "initialized": user_count > 0,
                "user_count": user_count
            },
            "message": "服务已就绪"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "database": {
                    "type": DatabaseCompatibility.get_db_type(),
                    "initialized": False,
                    "error": str(e)
                },
                "message": "服务未就绪"
            }
        )