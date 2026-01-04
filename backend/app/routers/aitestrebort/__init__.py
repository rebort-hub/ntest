"""
aitestrebort 集成模块 - 路由
基于 FastAPI 路由系统
"""
from .project import router as project_router
from .testcase import router as testcase_router
from .automation import router as automation_router
from .ai_generator import router as ai_router
from .global_config import router as global_router
from .knowledge import router as knowledge_router
from .requirements import router as requirements_router
from .orchestrator import router as orchestrator_router
from .advanced_features import router as advanced_features_router

__all__ = [
    'project_router',
    'testcase_router', 
    'automation_router',
    'ai_router',
    'global_router',
    'knowledge_router',
    'requirements_router',
    'orchestrator_router',
    'advanced_features_router'
]