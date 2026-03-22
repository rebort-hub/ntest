from fastapi import Request, Depends


from ...models.system.model_factory import SystemErrorRecord
from ...schemas.system import error_record as schema

async def get_error_record_list(request: Request, form: schema.GetSystemErrorRecordList = Depends()):
    get_filed = ["id", "create_time", "create_user", "method", "url"]
    query_data = await form.make_pagination(SystemErrorRecord, get_filed=get_filed)
    return request.app.get_success(data=query_data)

async def get_error_record(request: Request, form: schema.GetSystemErrorRecordForm = Depends()):
    data = await SystemErrorRecord.validate_is_exist("数据不存在", id=form.id)
    return request.app.get_success(data=data)
