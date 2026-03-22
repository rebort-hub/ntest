from fastapi import Request, Depends

from ...models.config.model_factory import BusinessLine
from ...models.system.user import User
from ...schemas.config import business as schema


async def get_business_list(request: Request, form: schema.FindBusinessLineForm = Depends()):
    get_filed = BusinessLine.get_simple_filed_list()
    if form.detail:
        get_filed.extend(["code", "desc", "create_user"])
    query_data = await form.make_pagination(BusinessLine, user=request.state.user, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def batch_to_user(request: Request, form: schema.BusinessToUserForm):
    await BusinessLine.business_to_user(form.business_list, form.user_list, form.command)
    return request.app.put_success()


async def change_business_sort(request: Request, form: schema.ChangeSortForm):
    await BusinessLine.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def get_business_detail(request: Request, form: schema.GetBusinessForm = Depends()):
    business = await BusinessLine.validate_is_exist("业务线不存在", id=form.id)
    return request.app.get_success(business)


async def add_business(request: Request, form: schema.PostBusinessForm):
    await form.validate_request(request)
    business = await BusinessLine.model_create(form.dict(), request.state.user)

    # 给创建者添加绑定关系
    request.state.user.business_list.append(business.id)
    await User.filter(id=request.state.user.id).update(business_list=request.state.user.business_list)

    # 重新生成token
    user = await User.filter(id=request.state.user.id).first()
    token = user.make_access_token(
        request.state.user.api_permissions, request.app.conf.access_token_time_out, request.app.conf.token_secret_key)
    return request.app.post_success(data={"token": token, "business_id": user.business_list})


async def change_business(request: Request, form: schema.PutBusinessForm):
    await BusinessLine.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def delete_business(request: Request, form: schema.GetBusinessForm):
    await User.validate_is_not_exist("业务线被用户引用，请先解除", business_list__icontains=form.id)
    await BusinessLine.filter(id=form.id).delete()
    return request.app.delete_success()
