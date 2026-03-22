from fastapi import Request, Depends

from ...schemas.system import role as schema
from ...models.system.model_factory import Role, UserRoles, User, Permission, RolePermissions


async def get_role_list(request: Request, form: schema.FindRoleForm = Depends()):
    get_filed = Role.get_simple_filed_list()
    if form.detail:
        get_filed.extend(["desc", "create_time", "update_time"])

    # 如果不是管理员，则不返回管理员角色
    role_id_list = []
    if User.is_not_admin(request.state.user.api_permissions):
        # 管理员权限
        admin_permission = [p["id"] for p in await Permission.filter(source_addr="admin").all().values("id")]
        # 没有管理员权限的角色
        not_admin_roles = await RolePermissions.filter(permission_id__not_in=admin_permission).distinct().values("role_id")
        role_id_list = [role["role_id"] for role in not_admin_roles]

    query_data = await form.make_pagination(Role, role_id_list=role_id_list, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def change_role_sort(request: Request, form: schema.ChangeSortForm):
    await Role.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def get_role_detail(request: Request, form: schema.GetRoleForm = Depends()):
    role = await Role.validate_is_exist("角色不存在", id=form.id)
    permissions = await User.get_role_permissions([form.id])
    return request.app.get_success(data={"data": role, **permissions})


async def add_role(request: Request, form: schema.CreateRoleForm):
    data = form.dict()
    front_permission, api_permission = data.pop("front_permission"), data.pop("api_permission")
    data["max_num"] = await Role.get_max_num() + 1
    role = await Role.model_create(data, request.state.user)
    await role.insert_role_permissions([*front_permission, *api_permission])
    return request.app.post_success()


async def change_role(request: Request, form: schema.EditRoleForm):
    role = await Role.validate_is_exist("数据不存在", id=form.id)
    data = form.dict()
    front_permission, api_permission = data.pop("front_permission"), data.pop("api_permission")
    await role.model_update(data, request.state.user)
    await role.update_role_permissions([*front_permission, *api_permission])
    return request.app.put_success()


async def delete_role(request: Request, form: schema.GetRoleForm):
    role = await Role.validate_is_exist("角色不存在", id=form.id)
    await UserRoles.validate_is_not_exist("角色已被用户引用，请先解除引用", role_id=form.id)
    await role.delete_role_permissions()
    await role.model_delete()
    return request.app.delete_success()
