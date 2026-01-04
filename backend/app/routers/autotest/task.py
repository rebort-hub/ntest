from typing import List

from ...models.autotest.model_factory import ApiTaskPydantic as TaskPydantic

from ..base_view import APIRouter
from ...services.autotest import task as task_service

task_router = APIRouter()

task_router.add_get_route(
    "/list", task_service.get_task_list, response_model=List[TaskPydantic], summary="获取任务列表")
task_router.add_put_route("/sort", task_service.change_task_sort, summary="任务列表排序")
task_router.add_post_route("/copy", task_service.copy_task, summary="复制定时任务")
task_router.add_get_route("", task_service.get_task_detail, summary="获取任务详情")
task_router.add_post_route("", task_service.add_task, summary="新增任务")
task_router.add_put_route("", task_service.change_task, summary="修改任务")
task_router.add_delete_route("", task_service.delete_task, summary="删除任务")
task_router.add_post_route("/status", task_service.enable_task, summary="启用定时任务")
task_router.add_delete_route("/status", task_service.disable_task, summary="关闭定时任务")
task_router.add_post_route("/run", task_service.run_task, auth=False, summary="运行任务")
