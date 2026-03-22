from typing import List

from ...models.autotest.model_factory import ApiCasePydantic as CasePydantic
from ...services.autotest import case as case_service
from ..base_view import APIRouter

case_router = APIRouter()

case_router.add_get_route(
    "/list", case_service.get_case_list, response_model=List[CasePydantic], summary="获取用例列表")
case_router.add_put_route("/sort", case_service.change_case_sort, summary="用例排序")
case_router.add_get_route("/make-data-list", case_service.get_make_data_case_list, summary="获取造数用例集的用例list")
case_router.add_get_route("/name", case_service.get_case_name, summary="根据用例id获取用例名")
case_router.add_get_route("/project", case_service.get_case_project, summary="获取用例属于哪个用例集、哪个用例")
case_router.add_put_route("/status", case_service.change_case_status, summary="修改用例状态（是否执行）")
case_router.add_put_route("/parent", case_service.change_case_parent, summary="修改用例的归属")
case_router.add_post_route("/copy", case_service.copy_case, summary="复制用例")
case_router.add_post_route("/copy-step", case_service.case_copy_step, summary="复制指定步骤到当前用例下")
case_router.add_get_route("/from", case_service.case_from, summary="获取用例的归属")
case_router.add_get_route("", case_service.get_case_detail, summary="获取用例详情")
case_router.add_post_route("", case_service.add_case, summary="新增用例")
case_router.add_put_route("", case_service.change_case, summary="修改用例")
case_router.add_delete_route("", case_service.delete_case, summary="删除用例")
case_router.add_post_route("/run", case_service.run_case, summary="运行测试用例")
