from ..base_view import APIRouter
from ...services.tools import mock_data as mock_data_service

mock_data_router = APIRouter()

mock_data_router.add_get_route(
    "", mock_data_service.mock_data_by_request_get, auth=False, summary="模拟接口处理，收到什么就返回什么")
mock_data_router.add_post_route(
    "", mock_data_service.mock_data_by_request_post, auth=False, summary="模拟接口处理，收到什么就返回什么")
mock_data_router.add_put_route(
    "", mock_data_service.mock_data_by_request_put, auth=False, summary="模拟接口处理，收到什么就返回什么")
mock_data_router.add_delete_route(
    "", mock_data_service.mock_data_by_request_delete, auth=False, summary="模拟接口处理，收到什么就返回什么")

mock_data_router.add_get_route(
    "/<script_name>", mock_data_service.mock_data_by_script_get, auth=False, summary="python脚本处理mock机制")
mock_data_router.add_post_route(
    "/<script_name>", mock_data_service.mock_data_by_script_post, auth=False, summary="python脚本处理mock机制")
mock_data_router.add_put_route(
    "/<script_name>", mock_data_service.mock_data_by_script_put, auth=False, summary="python脚本处理mock机制")
mock_data_router.add_delete_route(
    "/<script_name>", mock_data_service.mock_data_by_script_delete, auth=False, summary="python脚本处理mock机制")
