from ...services.autotest import element as element_service
from ..base_view import APIRouter

element_router = APIRouter()

element_router.add_get_route("/list", element_service.get_element_list, summary="获取元素列表")
element_router.add_put_route("/sort", element_service.change_element_sort, summary="元素列表排序")
element_router.add_put_route("/id", element_service.change_element_by_id, summary="根据id修改元素")
element_router.add_get_route("/from", element_service.get_element_from, summary="获取元素的归属信息")
element_router.add_get_route("/template/download", element_service.get_element_template, summary="下载元素导入模板")
element_router.add_post_route("/upload", element_service.element_upload, summary="从excel中导入元素")
element_router.add_get_route("", element_service.get_element_detail, summary="获取元素详情")
element_router.add_post_route("", element_service.add_element, summary="新增元素")
element_router.add_put_route("", element_service.change_element, summary="修改元素")
element_router.add_delete_route("", element_service.delete_element, summary="删除元素")
