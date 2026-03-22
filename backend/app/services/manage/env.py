from fastapi import Request, Depends

from ...models.manage.model_factory import Env
from ...schemas.manage import env as schema


async def get_env_list(request: Request, form: schema.GetEnvListForm = Depends()):
    get_filed = ["id", "business", "name", "value", "desc"]
    query_data = await form.make_pagination(Env, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def change_env_sort(request: Request, form: schema.ChangeSortForm):
    await Env.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def copy_env(request: Request, form: schema.GetEnvForm):
    data = await Env.validate_is_exist("数据不存在", id=form.id)
    await data.copy()
    return request.app.put_success()


async def get_env_detail(request: Request, form: schema.GetEnvForm = Depends()):
    env = await Env.validate_is_exist("数据不存在", id=form.id)
    return request.app.get_success(data=env)


async def add_env(request: Request, form: schema.AddEnvForm):
    data_list = await form.validate_request(request)
    await Env.bulk_create([Env(create_user=request.state.user.id, **env) for env in data_list])
    return request.app.post_success()


async def change_env(request: Request, form: schema.ChangeEnvForm):
    await Env.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def delete_env(request: Request, form: schema.GetEnvForm):
    await Env.filter(id=form.id).delete()
    return request.app.delete_success()


async def get_account_list(request: Request, form: schema.GetAccountListForm = Depends()):
    get_filed = ["id", "name", "value", "password", "desc"]
    query_data = await form.make_pagination(Env, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def change_account_sort(request: Request, form: schema.ChangeSortForm):
    await Env.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def get_account_detail(request: Request, form: schema.GetAccountForm = Depends()):
    env = await Env.validate_is_exist("数据不存在", id=form.id)
    return request.app.get_success(data=env)


async def add_account(request: Request, form: schema.AddAccountForm):
    data_list = await form.validate_request(request)
    await Env.bulk_create([Env(create_user=request.state.user.id, **env) for env in data_list])
    return request.app.post_success()


async def change_account(request: Request, form: schema.ChangeAccountForm):
    await Env.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def delete_account(request: Request, form: schema.GetAccountForm):
    await Env.filter(id=form.id).delete()
    return request.app.delete_success()
