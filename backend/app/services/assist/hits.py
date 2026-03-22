from fastapi import Request, Depends

from ...models.assist.model_factory import Hits
from ...schemas.assist import hits as schema


async def get_hit_type_list(request: Request):
    type_list = await Hits.all().distinct().values("hit_type")
    return request.app.get_success(data=[{"key": data["hit_type"], "value": data["hit_type"]} for data in type_list])


async def get_hit_list(request: Request, form: schema.GetHitListForm = Depends()):
    get_filed = [
        "id", "date", "project_id", "test_type", "env", "hit_type", "hit_detail", "report_id", "record_from",
        "create_user"
    ]
    query_data = await form.make_pagination(Hits, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def get_hit_detail(request: Request, form: schema.GetHitForm = Depends()):
    data = await Hits.validate_is_exist("数据不存在", id=form.id)
    return request.app.get_success(data)


async def add_hit(request: Request, form: schema.CreatHitForm):
    await form.validate_request()
    hit = await Hits.model_create(form.dict(), request.state.user)
    return request.app.post_success(data=hit)


async def change_hit(request: Request, form: schema.EditHitForm):
    await Hits.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def delete_hit(request: Request, form: schema.DeleteHitForm):
    await Hits.filter(id__in=form.id_list).delete()
    return request.app.delete_success()
