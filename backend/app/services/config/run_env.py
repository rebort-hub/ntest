from fastapi import Request, Depends

from ...models.config.model_factory import RunEnv, RunEnvPydantic, BusinessLine
from ...models.autotest.model_factory import ApiProject, ApiProjectEnv, AppProject, AppProjectEnv, UiProject, \
    UiProjectEnv

from ...schemas.config import run_env as schema


async def get_run_env_list(request: Request, form: schema.GetRunEnvListForm = Depends()):
    validate_filter = {}
    if form.business_id:
        validate_filter = {"id__in": await BusinessLine.get_env_list(form.business_id)}

    get_filed = ["code", "group", *RunEnv.get_simple_filed_list()]
    if form.detail:
        get_filed.append("desc")
    query_data = await form.make_pagination(RunEnv, validate_filter=validate_filter, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def batch_to_business(request: Request, form: schema.EnvToBusinessForm):
    await RunEnv.env_to_business(form.env_list, form.business_list, form.command)
    return request.app.put_success()


async def get_run_env_group(request: Request):
    group_list = await RunEnv.all().distinct().values("group")
    return request.app.get_success(data=[data["group"] for data in group_list])


async def change_run_env_sort(request: Request, form: schema.ChangeSortForm):
    await RunEnv.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def get_run_env_detail(request: Request, form: schema.GetRunEnvForm = Depends()):
    env = await RunEnv.validate_is_exist("环境不存在", id=form.id)
    return request.app.get_success(env)


async def add_run_env(request: Request, form: schema.PostRunEnvForm):
    await form.validate_request()
    max_num = await RunEnv.get_max_num()
    for index, add_env in enumerate(form.env_list):
        add_data = add_env.dict()
        add_data["num"] = max_num + index + 1
        run_env = await RunEnv.model_create(add_data, request.state.user)

        # 给所有的服务/项目/app创建此运行环境的数据
        await ApiProjectEnv.add_env(run_env.id, ApiProject)
        await UiProjectEnv.add_env(run_env.id, UiProject)
        await AppProjectEnv.add_env(run_env.id, AppProject)

        # 把环境分配给设置了自动绑定的业务线
        business_list = await BusinessLine.get_auto_bind_env_id_list()
        await RunEnv.env_to_business([run_env.id], business_list, "add")

    return request.app.post_success()


async def change_run_env(request: Request, form: schema.PutRunEnvForm):
    await RunEnv.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def delete_run_env(request: Request, form: schema.GetRunEnvForm):
    await RunEnv.filter(id=form.id).delete()
    return request.app.delete_success()
