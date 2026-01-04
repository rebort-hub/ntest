from ..base_view import APIRouter
from ...services.config import webhook as webhook_service

webhook_router = APIRouter()

webhook_router.add_get_route("/list", webhook_service.get_webhook_list, summary="获取webhook列表")
webhook_router.add_put_route("/sort", webhook_service.change_webhook_sort, summary="修改排序")
webhook_router.add_post_route("/debug", webhook_service.debug_webhook, summary="调试webhook")
webhook_router.add_get_route("", webhook_service.get_webhook, summary="获取webhook")
webhook_router.add_post_route("", webhook_service.add_webhook, summary="新增webhook")
webhook_router.add_put_route("", webhook_service.change_webhook, summary="修改webhook")
webhook_router.add_delete_route("", webhook_service.delete_webhook, summary="删除webhook")
