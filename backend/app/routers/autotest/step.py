from typing import List

from ...models.autotest.model_factory import ApiStepPydantic as StepPydantic
from ...services.autotest import step as step_service
from ..base_view import APIRouter

step_router = APIRouter()

step_router.add_get_route(
    "/list", step_service.get_step_list, response_model=List[StepPydantic], summary="获取步骤列表")
step_router.add_get_route(
    "/execute-mapping", step_service.get_step_execute_mapping, summary="获取执行动作类型列表(APP、UI)")
step_router.add_get_route(
    "/extract-mapping", step_service.get_step_extract_mapping, summary="数据提取方法列表(APP、UI)")
step_router.add_get_route(
    "/assert-mapping", step_service.get_step_assert_mapping, summary="数据断言方法列表(APP、UI)")
step_router.add_get_route(
    "/key-board-code", step_service.get_step_key_board_code, summary="获取键盘映射(UI)")
step_router.add_put_route("/sort", step_service.change_step_sort, summary="步骤排序")
step_router.add_put_route("/status", step_service.change_step_status, summary="修改步骤状态（是否执行）")
step_router.add_post_route("/copy", step_service.copy_step, summary="复制步骤")
step_router.add_put_route("/element", step_service.change_step_element, summary="修改步骤的接口/元素")
step_router.add_get_route("", step_service.get_step_detail, summary="获取步骤详情")
step_router.add_post_route("", step_service.add_step, summary="新增步骤")
step_router.add_put_route("", step_service.change_step, summary="修改步骤")
step_router.add_delete_route("", step_service.delete_step, summary="删除步骤")
