import traceback

from fastapi import Request, Depends

from ...models.config.model_factory import WebHook
from app.schemas.enums import WebHookTypeEnum
from utils.message.template import debug_msg_ding_ding, debug_msg_we_chat
from ...schemas.config import webhook as schema
from utils.logs.log import logger

async def get_webhook_list(request: Request, form: schema.GetWebHookListForm = Depends()):
    get_filed = ["id", "name", "webhook_type"]
    if form.detail:
        get_filed.extend(["addr", "desc"])
    query_data = await form.make_pagination(WebHook, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def change_webhook_sort(request: Request, form: schema.ChangeSortForm):
    await WebHook.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def debug_webhook(request: Request, form: schema.GetWebHookForm):
    webhook = await WebHook.validate_is_exist("数据不存在", id=form.id)
    match webhook.webhook_type.value:
        case WebHookTypeEnum.DING_DING:
            msg = debug_msg_ding_ding()
        case WebHookTypeEnum.WE_CHAT:
            msg = debug_msg_we_chat()
        case _:
            return request.app.fail("webhook类型暂不支持")
    try:
        return request.app.success(f"测试通过：{await webhook.debug(msg)}")
    except Exception as e:
        logger.error(traceback.format_exc())
        return request.app.fail("调试触发失败，请检查地址是否正确，网络是否通畅")


async def get_webhook(request: Request, form: schema.GetWebHookForm = Depends()):
    webhook = await WebHook.validate_is_exist("数据不存在", id=form.id)
    return request.app.get_success(webhook)


async def add_webhook(request: Request, form: schema.PostWebHookForm):
    data_list, max_num = [], await WebHook.get_max_num()
    for index, data in enumerate(form.data_list):
        insert_data = data.dict()
        insert_data["num"] = max_num + index + 1
        data_list.append(insert_data)
    await WebHook.batch_insert(data_list, request.state.user)
    return request.app.post_success()


async def change_webhook(request: Request, form: schema.PutWebHookForm):
    await WebHook.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def delete_webhook(request: Request, form: schema.GetWebHookForm):
    await WebHook.filter(id=form.id).delete()
    return request.app.delete_success()
