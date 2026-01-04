from ..base_view import APIRouter

config_router = APIRouter()

from app.routers.config.config import conf_router
from app.routers.config.run_env import run_env_router
from app.routers.config.business import business_router
from app.routers.config.webhook import webhook_router

config_router.include_router(conf_router, prefix="", tags=["配置管理"])
config_router.include_router(run_env_router, prefix="/run-env", tags=["运行环境管理"])
config_router.include_router(business_router, prefix="/business", tags=["业务线管理"])
config_router.include_router(webhook_router, prefix="/webhook", tags=["webhook管理"])
