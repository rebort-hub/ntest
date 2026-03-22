from ..base_view import APIRouter
from ...services.tools import make_user as make_user_service

make_user_router = APIRouter()

make_user_router.add_post_route("", make_user_service.make_user_list, summary="生成用户信息")
make_user_router.add_post_route(
    "/contact/download", make_user_service.make_contact_list, summary="导出为通讯录文件")
