from fastapi import Request, Depends

from ...models.assist.model_factory import FuncErrorRecord
from ...schemas.assist import error_record as schema


async def get_error_record_list(request: Request, form: schema.FindErrorForm = Depends()):
    get_filed = ["id", "name", "create_time", "create_user"]
    query_data = await form.make_pagination(FuncErrorRecord, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def get_error_record(request: Request, form: schema.GetErrorForm = Depends()):
    data = await FuncErrorRecord.validate_is_exist("数据不存在", id=form.id)
    return request.app.get_success(data=data)
