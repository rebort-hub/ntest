from fastapi import Request, Depends

from ...schemas.system import permission as schema
from ...models.system.model_factory import Permission, RolePermissions


async def get_permission_type(request: Request):
    return request.app.get_success(data={"api": '接口地址', "front": '前端地址'})


async def get_permission_list(request: Request, form: schema.GetPermissionListForm = Depends()):
    get_filed = ["id", "name", "source_type"]
    if form.detail:
        get_filed.extend(["source_addr", "desc", "create_time"])
    query_data = await form.make_pagination(Permission)
    return request.app.get_success(data=query_data)


async def change_permission_sort(request: Request, form: schema.ChangeSortForm):
    await Permission.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def get_permission_detail(request: Request, form: schema.GetPermissionForm = Depends()):
    permission = await Permission.validate_is_exist("数据不存在", id=form.id)
    return request.app.get_success(permission)


async def add_permission(request: Request, form: schema.CreatePermissionForm):
    data_list, max_num = [], await Permission.get_max_num()
    for index, data in enumerate(form.data_list):
        add_data = data.dict()
        add_data["num"] = max_num + index + 1
        data_list.append(add_data)
    await Permission.batch_insert(data_list, request.state.user)
    return request.app.post_success()


async def change_permission(request: Request, form: schema.EditPermissionForm):
    await Permission.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def remove_permission(request: Request, form: schema.GetPermissionForm):
    await RolePermissions.validate_is_not_exist("权限已被角色引用，请先解除引用", permission_id=form.id)
    await Permission.filter(id=form.id).delete()
    return request.app.delete_success()
