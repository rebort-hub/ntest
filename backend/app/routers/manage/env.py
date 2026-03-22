from ..base_view import APIRouter
from ...services.manage import env as env_service

env_router = APIRouter()

env_router.add_get_route("/list", env_service.get_env_list, summary="获取数据列表")
env_router.add_put_route("/sort", env_service.change_env_sort, summary="修改数据排序")
env_router.add_post_route("/copy", env_service.copy_env, summary="复制数据")
env_router.add_get_route("", env_service.get_env_detail, summary="获取数据详情")
env_router.add_post_route("", env_service.add_env, summary="新增数据")
env_router.add_put_route("", env_service.change_env, summary="修改数据")
env_router.add_delete_route("", env_service.delete_env, summary="删除数据")

env_router.add_get_route("/account/list", env_service.get_account_list, summary="获取数据列表")
env_router.add_put_route("/account/sort", env_service.change_account_sort, summary="修改数据排序")
env_router.add_get_route("/account", env_service.get_account_detail, summary="获取数据详情")
env_router.add_post_route("/account", env_service.add_account, summary="新增数据")
env_router.add_put_route("/account", env_service.change_account, summary="修改数据")
env_router.add_delete_route("/account", env_service.delete_account, summary="删除数据")
