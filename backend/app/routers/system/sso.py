from ..base_view import APIRouter
from ...services.system import sso as sso_service

sso_router = APIRouter()

sso_router.add_get_route("/redirect-uri", sso_service.get_sso_redirect_uri, summary="获取重定向的登录地址")
sso_router.add_get_route("/token", sso_service.login_by_sso_code, summary="使用sso获取到的code登录")
