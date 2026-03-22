from ..base_view import APIRouter
from ...services.system import role as role_service

role_router = APIRouter()

role_router.add_get_route("/list", role_service.get_role_list, summary="获取角色列表")
role_router.add_put_route("/sort", role_service.change_role_sort, summary="修改排序")
role_router.add_get_route("", role_service.get_role_detail, summary="获取角色详情")
role_router.add_post_route("", role_service.add_role, summary="新增角色")
role_router.add_put_route("", role_service.change_role, summary="修改角色")
role_router.add_delete_route("", role_service.delete_role, summary="删除角色")



