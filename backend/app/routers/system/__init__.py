from ..base_view import APIRouter

system_router = APIRouter()

from app.routers.system.error_record import error_record_router
from app.routers.system.job import job_router
from app.routers.system.package import package_router
from app.routers.system.permission import permission_router
from app.routers.system.role import role_router
from app.routers.system.sso import sso_router
from app.routers.system.user import user_router

system_router.include_router(error_record_router, prefix="/error-record", tags=["系统错误记录"])
system_router.include_router(job_router, prefix="/job", tags=["系统任务管理"])
system_router.include_router(package_router, prefix="/package", tags=["python包管理"])
system_router.include_router(permission_router, prefix="/permission", tags=["权限管理"])
system_router.include_router(role_router, prefix="/role", tags=["角色管理"])
system_router.include_router(sso_router, prefix="/sso", tags=["sso登录"])
system_router.include_router(user_router, prefix="/user", tags=["用户管理"])
