from ..base_view import APIRouter
from ...services.autotest import device as service

device_router = APIRouter()

device_router.add_get_route("/server/list", service.get_server_list, summary="获取运行服务器列表")
device_router.add_put_route("/server/sort", service.change_server_sort, summary="运行服务器排序")
device_router.add_post_route("/server/copy", service.copy_server, summary="复制运行服务器")
device_router.add_post_route("/server/run", service.run_server, summary="连接运行服务器")
device_router.add_get_route("/server", service.get_server_detail, summary="获取运行服务器详情")
device_router.add_post_route("/server", service.add_server, summary="新增运行服务器")
device_router.add_put_route("/server", service.change_server, summary="修改运行服务器")
device_router.add_delete_route("/server", service.delete_server, summary="删除运行服务器")

device_router.add_get_route("/phone/list", service.get_phone_list, summary="获取运行设备列表")
device_router.add_put_route("/phone/sort", service.change_phone_sort, summary="运行设备排序")
device_router.add_post_route("/phone/copy", service.copy_phone, summary="复制运行设备")
device_router.add_get_route("/phone", service.get_phone_detail, summary="获取运行设备详情")
device_router.add_post_route("/phone", service.add_phone, summary="新增运行设备")
device_router.add_put_route("/phone", service.change_phone, summary="修改运行设备")
device_router.add_delete_route("/phone", service.delete_phone, summary="删除运行设备")
