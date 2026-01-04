from ..base_view import APIRouter
from ...services.assist import data_pool as data_pool_service

data_pool_router = APIRouter()

data_pool_router.add_get_route(
    "/auto-test-user", data_pool_service.get_auto_test_user_list, summary="获取自动化测试用户数据列表")
data_pool_router.add_get_route(
    "/business-status", data_pool_service.get_data_pool_business_status, summary="获取数据池业务状态")
data_pool_router.add_get_route("/list", data_pool_service.get_data_pool_list, summary="获取数据池列表")
data_pool_router.add_get_route("/use-status", data_pool_service.get_data_pool_use_status, summary="获取数据池使用状态")
data_pool_router.add_get_route("", data_pool_service.get_data_pool_detail, summary="获取数据详情")
data_pool_router.add_post_route("", data_pool_service.add_data_pool, summary="新增数据")
data_pool_router.add_put_route("", data_pool_service.change_data_pool, summary="修改数据")
data_pool_router.add_delete_route("", data_pool_service.delete_data_pool, summary="删除数据")
