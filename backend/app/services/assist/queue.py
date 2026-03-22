from fastapi import Request, Depends

from ...models.assist.model_factory import QueueInstance, QueueTopic, QueueMsgLog
from ...schemas.assist import queue as schema
from ...schemas.enums import QueueTypeEnum
from utils.message.send_mq import send_rabbit_mq, send_rocket_mq, send_active_mq


async def get_queue_instance_list(request: Request, form: schema.GetQueueInstanceListForm = Depends()):
    get_filed = ["id", "queue_type", "host", "port", "desc", "instance_id", "create_user"]
    data = await form.make_pagination(QueueInstance, get_filed=get_filed)
    return request.app.get_success(data)


async def change_queue_instance_sort(request: Request, form: schema.ChangeSortForm):
    await QueueInstance.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def get_queue_instance(request: Request, form: schema.GetQueueInstanceForm = Depends()):
    data = await QueueInstance.validate_is_exist("数据不存在", id=form.id)
    queue_instance_dict = dict(data)
    queue_instance_dict.pop('account')
    queue_instance_dict.pop('password')
    queue_instance_dict.pop('access_id')
    queue_instance_dict.pop('access_key')
    return request.app.get_success(queue_instance_dict)


async def add_queue_instance(request: Request, form: schema.CreatQueueInstanceForm):
    await QueueInstance.model_create(form.dict(), request.state.user)
    return request.app.post_success()


async def change_queue_instance(request: Request, form: schema.EditQueueInstanceForm):
    await QueueInstance.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def get_queue_topic_list(request: Request, form: schema.GetQueueTopicListForm = Depends()):
    get_filed = ["id",  "instance_id",  "topic",  "desc",  "create_user"]
    data = await form.make_pagination(QueueTopic, get_filed=get_filed)
    return request.app.get_success(data)


async def change_queue_topic_sort(request: Request, form: schema.ChangeSortForm):
    await QueueTopic.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def copy_queue_topic(request: Request, form: schema.GetQueueTopicForm):
    data = await QueueTopic.validate_is_exist("数据不存在", id=form.id)
    await data.copy()
    return request.app.copy_success()


async def get_queue_topic(request: Request, form: schema.GetQueueTopicForm = Depends()):
    data = await QueueTopic.validate_is_exist("数据不存在", id=form.id)
    return request.app.get_success(data)


async def add_queue_topic(request: Request, form: schema.CreatQueueTopicForm):
    await QueueTopic.model_create(form.dict(), request.state.user)
    return request.app.post_success()


async def change_queue_topic(request: Request, form: schema.EditQueueTopicForm):
    await QueueTopic.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def delete_queue_topic(request: Request, form: schema.GetQueueTopicForm):
    await QueueTopic.filter(id=form.id).delete()
    return request.app.delete_success()


async def send_message_to_queue(request: Request, form: schema.SendMessageForm):
    queue_topic = await QueueTopic.validate_is_exist('数据不存在', id=form.id)

    queue_instance = await QueueInstance.filter(id=queue_topic.instance_id).first().values(
        "id", "queue_type", "host", "port", "account", "password", "access_id", "access_key", "instance_id")
    if not queue_instance or not queue_instance.get("id"):
        ValueError("数据不存在")

    match queue_instance["queue_type"]:
        case QueueTypeEnum.RABBIT_MQ:
            send_res = send_rabbit_mq(
                queue_instance["host"],
                queue_instance["port"],
                queue_instance["account"],
                queue_instance["password"],
                queue_topic.topic,
                form.message
            )
        case QueueTypeEnum.ROCKET_MQ:
            send_res = send_rocket_mq(
                queue_instance["host"],
                queue_instance["access_id"],
                queue_instance["access_key"],
                queue_topic.topic,
                queue_instance["instance_id"],
                form.message,
                form.tag,
                form.options
            )
        case QueueTypeEnum.ACTIVE_MQ:
            send_res = send_active_mq(
                queue_instance["host"],
                queue_instance["port"],
                queue_instance["account"],
                queue_instance["password"],
                queue_instance["instance_id"],
                queue_topic.topic,
                form.message
            )
        case _:
            return request.app.fail("不支持当前队列")
    await QueueMsgLog.model_create({
        "instance_id": queue_instance["id"],
        "topic_id": form.id,
        "tag": form.tag,
        "options": form.options,
        "message": form.message,
        "message_type": form.message_type,
        "status": send_res["status"],
        "response": send_res["res"]
    })
    return request.app.success('消息发送完成')


async def get_queue_log_list(request: Request, form: schema.GetQueueMsgLogForm = Depends()):
    get_filed = [
        "id", "topic_id", "tag", "options", "message_type", "message", "status", "response", "create_user", "create_time"
    ]
    data = await form.make_pagination(QueueMsgLog, get_filed=get_filed)
    return request.app.get_success(data)
