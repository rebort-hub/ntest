from ..base_view import APIRouter
from ...services.assist import call_back as call_back_service

call_back_router = APIRouter()

call_back_router.add_get_route("/list", call_back_service.get_call_back_list, summary="获取回调列表")
call_back_router.add_get_route("", call_back_service.get_call_back, summary="获取回调数据")
