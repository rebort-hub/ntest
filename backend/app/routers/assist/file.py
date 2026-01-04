from ..base_view import APIRouter
from ...services.assist import file as file_service

file_router = APIRouter()

file_router.add_get_route("/list", file_service.get_file_list, summary="获取文件列表")
file_router.add_get_route("/check", file_service.check_file_is_exists, summary="检查文件是否已存在")
file_router.add_get_route("/download", file_service.download_file, summary="下载文件")
# file_router.add_post_route("/upload", file_service.upload_file, summary="文件上传")
file_router.add_post_route("", file_service.batch_upload_file, summary="文件批量上传")
file_router.add_delete_route("", file_service.delete_file, summary="删除文件")
