from ..base_view import APIRouter
from ...services.system import permission as permission_service

permission_router = APIRouter()

permission_router.add_get_route("/list", permission_service.get_permission_list, summary="获取权限列表")
permission_router.add_get_route("/type", permission_service.get_permission_type, summary="获取权限类型")
permission_router.add_put_route("/sort", permission_service.change_permission_sort, summary="修改排序")
permission_router.add_get_route("", permission_service.get_permission_detail, summary="获取权限详情")
permission_router.add_post_route("", permission_service.add_permission, summary="新增权限")
permission_router.add_put_route("", permission_service.change_permission, summary="修改权限")
permission_router.add_delete_route("", permission_service.remove_permission, summary="删除权限")
