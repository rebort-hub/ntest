from fastapi import Request, Depends

from ...models.assist.model_factory import CallBack
from ...schemas.assist import call_back as schema


async def get_call_back_list(request: Request, form: schema.FindCallBackForm = Depends()):
    get_filed = ["id", "create_time", "url", "status"]
    query_data = await form.make_pagination(CallBack, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def get_call_back(request: Request, form: schema.GetCallBackForm = Depends()):
    call_back = await CallBack.validate_is_exist("", id=form.id)
    return request.app.get_success(data=call_back)
