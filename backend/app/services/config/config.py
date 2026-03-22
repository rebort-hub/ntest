from fastapi import Request, Depends

from ...schemas.config import config as schema
from ...models.config.model_factory import Config, ConfigType


async def get_config_type_list(request: Request, form: schema.GetConfigTypeListForm = Depends()):
    get_filed = ConfigType.get_simple_filed_list()
    if form.detail:
        get_filed.extend(["desc", "create_user"])
    query_data = await form.make_pagination(ConfigType, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def change_config_type_sort(request: Request, form: schema.ChangeSortForm):
    await ConfigType.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def get_config_type_detail(request: Request, form: schema.GetConfigTypeForm = Depends()):
    config_type = await ConfigType.validate_is_exist("配置类型不存在", id=form.id)
    return request.app.get_success(data=config_type)


async def add_config_type(request: Request, form: schema.PostConfigTypeForm):
    max_num = await ConfigType.get_max_num()
    data_list = [{
        "name": data.name, "desc": data.desc, "num": max_num + index + 1
    } for index, data in enumerate(form.data_list)]
    await ConfigType.batch_insert(data_list, request.state.user)
    return request.app.post_success()


async def change_config_type(request: Request, form: schema.PutConfigTypeForm):
    await ConfigType.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def delete_config_type(request: Request, form: schema.GetConfigTypeForm):
    await Config.validate_is_not_exist("配置类型被引用，不可删除", id=form.id)
    await ConfigType.filter(id=form.id).delete()
    return request.app.delete_success()


async def get_config_list(request: Request, form: schema.FindConfigForm = Depends()):
    get_filed = ConfigType.get_simple_filed_list()
    get_filed.append("value")
    if form.detail:
        get_filed.extend(["desc", "type", "update_user"])
    query_data = await form.make_pagination(Config, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def change_config_sort(request: Request, form: schema.ChangeSortForm):
    await Config.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def change_config_api_validator(request: Request, form: schema.AddApiDefaultValidatorConfigForm = Depends()):
    conf = await Config.filter(name='api_default_validator').first().values("value")
    conf_value = conf.loads(conf["value"])
    conf_value.append(form.model_dump())
    await Config.filter(name='api_default_validator').update(value=conf.dumps(conf_value))
    return request.app.put_success()


async def get_config_by_code(request: Request, form: schema.GetConfigForm = Depends()):
    conf = await Config.get_config_detail(form.id, form.code)
    return request.app.get_success(conf)


async def get_config_skip_if(request: Request, form: schema.GetSkipIfConfigForm = Depends()):
    data = [{"label": "运行环境", "value": "run_env"}]
    if form.test_type == "app":
        data += [{"label": "运行服务器", "value": "run_server"}, {"label": "运行设备", "value": "run_device"}]
    if form.type == "step":
        step_skip = [{"label": "自定义变量", "value": "variable"}, {"label": "自定义函数", "value": "func"}]
        return request.app.get_success(data=data + step_skip)
    return request.app.get_success(data=data)


async def get_config_find_element(request: Request, form: schema.GetFindElementByForm = Depends()):
    if form.test_type == "app":
        return request.app.get_success(data=await Config.get_find_element_by_app())
    return request.app.get_success(data=await Config.get_find_element_by_ui())


async def get_config_detail(request: Request, form: schema.GetConfigForm = Depends()):
    conf = await Config.get_config_detail(form.id, form.code)
    return request.app.get_success(conf)


async def add_config(request: Request, form: schema.PostConfigForm):
    await Config.model_create(form.dict(), request.state.user)
    return request.app.post_success()


async def change_config(request: Request, form: schema.PutConfigForm):
    await Config.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def delete_config(request: Request, form: schema.GetConfigByIdForm):
    await Config.filter(id=form.id).delete()
    return request.app.delete_success()
