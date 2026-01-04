from ..base_view import APIRouter
from ...services.assist import error_record as error_record_service

error_record_router = APIRouter()

error_record_router.add_get_route("-list", error_record_service.get_error_record_list, summary="获取错误列表")
error_record_router.add_get_route("", error_record_service.get_error_record, summary="获取错误详情")


