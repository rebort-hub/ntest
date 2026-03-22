from ..base_view import APIRouter
from ...services.manage import kym as kym_service

kym_router = APIRouter()

kym_router.add_get_route("/project-list", kym_service.get_kym_project_list, summary="kym服务列表")
kym_router.add_get_route("/download", kym_service.download_kym_as_xmind, summary="导出为xmind")
kym_router.add_post_route("/project", kym_service.add_kym_project, summary="kym添加服务")
kym_router.add_get_route("", kym_service.get_kym_detail, summary="获取KYM")
kym_router.add_put_route("", kym_service.change_kym, summary="修改KYM")

