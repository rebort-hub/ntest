from fastapi import Request, Depends

from ...models.assist.model_factory import AutoTestUser, DataPool
from ...schemas.assist import data_pool as schema


async def get_auto_test_user_list(request: Request, form: schema.GetAutoTestUserDataListForm = Depends()):
    get_filed = ["id", "mobile", "password", "access_token", "refresh_token", "company_name", "role", "env"]
    query_data = await form.make_pagination(AutoTestUser, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def get_data_pool_list(request: Request, form: schema.GetDataPoolListForm = Depends()):
    query_data = await form.make_pagination(DataPool, user=request.state.user)
    return request.app.get_success(data=query_data)


async def get_data_pool_business_status(request: Request):
    status = await DataPool.all().distinct().values("business_status")
    return request.app.get_success(data=[data["business_status"] for data in status])


async def get_data_pool_use_status(request: Request):
    return request.app.get_success(data={"not_used": "未使用", "in_use": "使用中", "used": "已使用"})


async def get_data_pool_detail(request: Request, form: schema.GetDataPoolForm = Depends()):
    data = await DataPool.validate_is_exist("数据不存在", id=form.id)
    return request.app.get_success(data)


async def add_data_pool(request: Request, form: schema.PostDataPoolForm):
    data_pool = await DataPool.model_create(form.dict(), request.state.user)
    return request.app.post_success(data=data_pool)


async def change_data_pool(request: Request, form: schema.PutDataPoolForm):
    await DataPool.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def delete_data_pool(request: Request, form: schema.GetDataPoolForm):
    await DataPool.filter(id=form.id).delete()
    return request.app.delete_success()
