from ...services.autotest import page as page_service
from ..base_view import APIRouter

page_router = APIRouter()

page_router.add_get_route("/list", page_service.get_page_list, summary="获取页面列表")
page_router.add_put_route("/sort", page_service.change_page_sort, summary="页面列表排序")
page_router.add_post_route("/copy", page_service.copy_page, summary="复制页面")
page_router.add_get_route("", page_service.get_page_detail, summary="获取页面详情")
page_router.add_post_route("", page_service.add_page, summary="新增页面")
page_router.add_put_route("", page_service.change_page, summary="修改页面")
page_router.add_delete_route("", page_service.delete_page, summary="删除页面")
