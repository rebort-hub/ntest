from ..base_view import APIRouter
from ...services.assist import hits as hits_service

hits_router = APIRouter()

hits_router.add_get_route("/type-list", hits_service.get_hit_type_list, summary="自动化测试命中问题类型列表")
hits_router.add_get_route("/list", hits_service.get_hit_list, summary="自动化测试命中问题列表")
hits_router.add_get_route("", hits_service.get_hit_detail, summary="获取自动化测试命中问题")
hits_router.add_post_route("", hits_service.add_hit, summary="新增自动化测试命中问题")
hits_router.add_put_route("", hits_service.change_hit, summary="修改自动化测试命中问题")
hits_router.add_delete_route("", hits_service.delete_hit, summary="删除自动化测试命中问题")
