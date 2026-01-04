from ..base_view import APIRouter
from ...services.assist import script as script_service

script_router = APIRouter()


script_router.add_get_route("/list", script_service.get_script_list, summary="获取脚本文件列表")
script_router.add_put_route("/sort", script_service.change_script_sort, summary="脚本文件列表排序")
script_router.add_post_route("/copy", script_service.copy_script, summary="复制自定义脚本文件")
script_router.add_post_route("/debug", script_service.debug_script, summary="函数调试")
script_router.add_get_route("", script_service.get_script, summary="获取脚本文件详情")
script_router.add_post_route("", script_service.add_script, summary="新增脚本文件")
script_router.add_put_route("", script_service.change_script, summary="修改脚本文件")
script_router.add_delete_route("", script_service.delete_script, summary="删除脚本文件")








