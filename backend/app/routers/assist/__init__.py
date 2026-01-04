from ..base_view import APIRouter

assist_router = APIRouter()

from app.routers.assist.call_back import call_back_router
from app.routers.assist.data_pool import data_pool_router
from app.routers.assist.error_record import error_record_router
from app.routers.assist.file import file_router
from app.routers.assist.hits import hits_router
from app.routers.assist.script import script_router
from app.routers.assist.swagger import swagger_router
from app.routers.assist.shell_command import shell_command_router
from app.routers.assist.queue import queue_router

assist_router.include_router(call_back_router, prefix="/call-back", tags=["回调管理"])
assist_router.include_router(data_pool_router, prefix="/data-pool", tags=["数据池管理"])
assist_router.include_router(error_record_router, prefix="/error-record", tags=["错误记录"])
assist_router.include_router(file_router, prefix="/file", tags=["文件管理"])
assist_router.include_router(hits_router, prefix="/hit", tags=["自动化测试不通过记录"])
assist_router.include_router(script_router, prefix="/script", tags=["自定义脚本管理"])
assist_router.include_router(swagger_router, prefix="/swagger", tags=["swagger拉取数据"])
assist_router.include_router(shell_command_router, prefix="/shell-command", tags=["shell造数据"])
assist_router.include_router(queue_router, prefix="", tags=["消息队列"])
