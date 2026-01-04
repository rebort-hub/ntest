from fastapi import Request, Depends

from ...models.autotest.model_factory import ApiModule, AppModule, UiModule, ApiMsg
from ...schemas.autotest import module as schema


async def get_module_list(request: Request, form: schema.FindModuleForm = Depends()):
    model = ApiModule if request.app.test_type == "api" else AppModule if request.app.test_type == "app" else UiModule
    get_filed = ["id", "name", "parent", "project_id"]
    query_data = await form.make_pagination(model, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def get_module_tree(request: Request, form: schema.GetModuleTreeForm = Depends()):
    model = ApiModule if request.app.test_type == "api" else AppModule if request.app.test_type == "app" else UiModule
    module_list = await model.filter(project_id=form.project_id).order_by("create_time").all()
    return request.app.get_success(data=module_list)

async def change_module_sort(request: Request, form: schema.ChangeSortForm):
    model = ApiModule if request.app.test_type == "api" else AppModule if request.app.test_type == "app" else UiModule
    await model.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()

async def get_module_detail(request: Request, form: schema.GetModuleForm = Depends()):
    model = ApiModule if request.app.test_type == "api" else AppModule if request.app.test_type == "app" else UiModule
    data = await model.filter(id=form.id).first()
    return request.app.get_success(data)


async def add_module(request: Request, form: schema.AddModuleForm):
    model = ApiModule if request.app.test_type == "api" else AppModule if request.app.test_type == "app" else UiModule
    max_num = await model.get_max_num()
    insert_list = [{
            "project_id": form.project_id,
            "parent": form.parent,
            "name": module_name,
            "num": max_num + index + 1
        } for index, module_name in enumerate(form.data_list)]
    await model.batch_insert(insert_list, request.state.user)
    return request.app.post_success()


async def change_module(request: Request, form: schema.EditModuleForm):
    model = ApiModule if request.app.test_type == "api" else AppModule if request.app.test_type == "app" else UiModule
    await model.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success(data=form.dict())


async def delete_module(request: Request, form: schema.GetModuleForm):
    model = ApiModule if request.app.test_type == "api" else AppModule if request.app.test_type == "app" else UiModule
    await model.validate_is_not_exist("请先删除当前模块下的子模块", parent=form.id)
    await ApiMsg.validate_is_not_exist("请先删除模块下的接口", module_id=form.id)
    await model.filter(id=form.id).delete()
    return request.app.delete_success()

