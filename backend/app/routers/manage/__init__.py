from ..base_view import APIRouter

manage_router = APIRouter()

from app.routers.manage.bug_track import bug_track_router
from app.routers.manage.env import env_router
from app.routers.manage.kym import kym_router
from app.routers.manage.todo import todo_router

manage_router.include_router(bug_track_router, prefix="/bug-track", tags=["线上问题跟踪"])
manage_router.include_router(env_router, prefix="/env", tags=["地址和账号管理"])
manage_router.include_router(kym_router, prefix="/kym", tags=["kym分析"])
manage_router.include_router(todo_router, prefix="/todo", tags=["待办管理"])
