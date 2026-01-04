from ...services.autotest import project as project_service

from ..base_view import APIRouter

project_router = APIRouter()

project_router.add_get_route("/list", project_service.get_project_list, summary="获取服务列表")
project_router.add_put_route("/sort", project_service.project_sort, summary="服务列表排序")
project_router.add_get_route("", project_service.get_project_detail, summary="获取服务详情")
project_router.add_post_route("", project_service.add_project, summary="新增服务")
project_router.add_put_route("", project_service.change_project, summary="修改服务")
project_router.add_delete_route("", project_service.delete_project, summary="删除服务")
project_router.add_get_route("/env", project_service.get_project_env, summary="获取服务环境")
project_router.add_put_route("/env", project_service.change_project_env, summary="修改服务环境")
project_router.add_put_route(
    "/env/synchronization", project_service.synchronization_project_env, summary="同步环境数据")
