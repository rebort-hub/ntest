from ..base_view import APIRouter
from ...services.assist import queue as queue_service

queue_router = APIRouter()

queue_router.add_get_route("/queue-instance/list", queue_service.get_queue_instance_list, summary="消息队列实例列表")
queue_router.add_put_route("/queue-instance/sort", queue_service.change_queue_instance_sort, summary="更新消息队列实例排序")
queue_router.add_get_route("/queue-instance", queue_service.get_queue_instance, summary="获取消息队列实例")
queue_router.add_post_route("/queue-instance", queue_service.add_queue_instance, summary="新增消息队列实例")
queue_router.add_put_route("/queue-instance", queue_service.change_queue_instance, summary="修改消息队列实例")

queue_router.add_get_route("/queue-topic/list", queue_service.get_queue_topic_list, summary="消息队列列表")
queue_router.add_put_route("/queue-topic/sort", queue_service.change_queue_topic_sort, summary="更新消息队列排序")
queue_router.add_post_route("/queue-topic/copy", queue_service.copy_queue_topic, summary="复制消息队列")
queue_router.add_get_route("/queue-topic", queue_service.get_queue_topic, summary="获取消息队列")
queue_router.add_post_route("/queue-topic", queue_service.add_queue_topic, summary="新增消息队列")
queue_router.add_put_route("/queue-topic", queue_service.change_queue_topic, summary="修改消息队列")
queue_router.add_delete_route("/queue-topic", queue_service.delete_queue_topic, summary="删除消息队列")
queue_router.add_post_route("/queue-topic/message", queue_service.send_message_to_queue, summary="发送消息队列")
queue_router.add_get_route("/queue-topic/log", queue_service.get_queue_log_list, summary="消息发送记录")
