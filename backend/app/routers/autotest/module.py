from ..base_view import APIRouter
from ...services.autotest import module as module_service

module_router = APIRouter()

module_router.add_get_route("/list", module_service.get_module_list, summary="获取模块列表")
module_router.add_get_route("/tree", module_service.get_module_tree, summary="获取服务下的模块树")
module_router.add_put_route("/sort", module_service.change_module_sort, summary="修改模块排序")
module_router.add_get_route("", module_service.get_module_detail, summary="获取模块详情")
module_router.add_post_route("", module_service.add_module, summary="新增模块")
module_router.add_put_route("", module_service.change_module, summary="修改模块")
module_router.add_delete_route("", module_service.delete_module, summary="删除模块")
