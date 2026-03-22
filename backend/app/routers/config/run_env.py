from ..base_view import APIRouter
from ...services.config import run_env as run_env_service

run_env_router = APIRouter()

run_env_router.add_get_route("/list", run_env_service.get_run_env_list, auth=False, summary="获取运行环境列表")
run_env_router.add_get_route("/group", run_env_service.get_run_env_group, summary="获取运行环境分组列表")
run_env_router.add_put_route("/sort", run_env_service.change_run_env_sort, summary="修改运行环境排序")
run_env_router.add_put_route(
    "/business", run_env_service.batch_to_business, summary="批量绑定/解除绑定运行环境与业务线的关系")
run_env_router.add_get_route("", run_env_service.get_run_env_detail, summary="获取运行环境详情")
run_env_router.add_post_route("", run_env_service.add_run_env, summary="新增运行环境")
run_env_router.add_put_route("", run_env_service.change_run_env, summary="修改运行环境")
run_env_router.add_delete_route("", run_env_service.delete_run_env, summary="删除运行环境")
