from ..base_view import APIRouter
from ...services.assist import shell_command as shell_command_service

shell_command_router = APIRouter()

shell_command_router.add_get_route(
    "/list", shell_command_service.get_shell_command_list, auth=False, summary="获取命令列表")
shell_command_router.add_get_route(
    "/record-list", shell_command_service.get_shell_command_record_list, auth=False, summary="获取造数据log列表")
shell_command_router.add_get_route(
    "/record", shell_command_service.get_shell_command_record, auth=False, summary="获取造数据log")
shell_command_router.add_post_route(
    "/send", shell_command_service.send_shell_command, auth=False, summary="发送造数据命令")
