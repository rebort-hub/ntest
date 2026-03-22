from ..base_view import APIRouter
from ...services.config import business as business_service

business_router = APIRouter()

business_router.add_get_route("/list", business_service.get_business_list, summary="获取业务线列表")
business_router.add_put_route("/sort", business_service.change_business_sort, summary="修改业务线排序")
business_router.add_put_route("/user", business_service.batch_to_user, summary="批量绑定/解除绑定业务线与用户的关系")
business_router.add_get_route("", business_service.get_business_detail, summary="获取业务线详情")
business_router.add_post_route("", business_service.add_business, summary="新增业务线")
business_router.add_put_route("", business_service.change_business, summary="修改业务线")
business_router.add_delete_route("", business_service.delete_business, summary="删除业务线")


