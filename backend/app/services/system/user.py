from fastapi import Request, Depends

from app.schemas.enums import DataStatusEnum
from ...models.system.model_factory import User, Role
from ...schemas.system import user as schema


async def get_user_list(request: Request, form: schema.FindUserForm = Depends()):
    # 非管理员，只能获取到当前用户有的业务线的人
    user_id_list = []
    if User.is_not_admin(request.state.user.api_permissions):
        user_id_set = set()
        for business_id in request.state.user.business_list:
            users = await User.filter(business_list__contains=business_id, id__not_in=list(user_id_set)).all().values("id")
            user_id_set = user_id_set.union({user["id"] for user in users})
        user_id_list = list(user_id_set)

    get_filed = ["id", "name", "email"]
    if form.detail:
        get_filed.extend(["account", "status", "create_time", "business_list", "sso_user_id"])
    query_data = await form.make_pagination(User, get_filed=get_filed, user_id_list=user_id_list)
    return request.app.get_success(data=query_data)


async def change_user_sort(request: Request, form: schema.ChangeSortForm):
    await User.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def get_user_detail(request: Request, form: schema.GetUserForm = Depends()):
    user = await User.validate_is_exist("用户不存在", id=form.id)
    return request.app.get_success(user)


async def add_user(request: Request, form: schema.CreateUserForm):
    user_list = await form.validate_request()
    max_num = await User.get_max_num()
    for index, data in enumerate(user_list):
        user = data.dict()
        user["num"] = max_num + index + 1
        role_list = user.pop("role_list")
        user["password"] = User.password_to_hash(user["password"], request.app.conf.password_secret_key)
        user = await User.model_create(user, request.state.user)
        await user.insert_user_roles(role_list)
    return request.app.post_success()


async def change_user(request: Request, form: schema.EditUserForm):
    await form.validate_request()
    user = await User.validate_is_exist("用户不存在", id=form.id)
    user_dict = form.dict()
    if user_dict.get("email_password") is None:
        user_dict.pop("email_password")
    role_list = user_dict.pop("role_list")
    await user.model_update(user_dict, request.state.user)
    await user.update_user_roles(role_list)
    return request.app.put_success()


async def delete_user(request: Request, form: schema.GetUserForm):
    form.validate_is_true(request.state.user.id != form.id, "不能自己删自己")
    user = await User.validate_is_exist("数据不存在", id=form.id)
    await user.delete_user_roles()
    await user.model_delete()
    return request.app.delete_success()


async def user_login(request: Request, form: schema.LoginForm):
    user = await User.filter(account=form.account).first()
    if user is None: return request.app.fail("账号或密码错误")
    form.validate_is_true(user.verify_password(form.password, request.app.conf.password_secret_key), "账号或密码错误")
    form.validate_is_true(user.status != DataStatusEnum.DISABLE, "账号为冻结状态，请联系管理员")

    user_info = await user.build_access_token(
            request.app.conf.access_token_time_out,
            request.app.conf.token_secret_key
        )
    user_info["refresh_token"] = user.make_refresh_token(
            request.app.conf.refresh_token_time_out,
            request.app.conf.token_secret_key
        )
    return request.app.success("登录成功", user_info)


async def refresh_token(request: Request):
    if user := User.check_token(request.headers.get("refresh-token", ""), request.app.conf.token_secret_key):
        user = await User.filter(id=user["user_id"]).first()
        user_info = await user.build_access_token(
            request.app.conf.refresh_token_time_out,
            request.app.conf.token_secret_key
        )
        return request.app.success(data=user_info)
    return request.app.not_login()


async def user_logout(request: Request):
    return request.app.success(msg="登出成功")


async def get_user_role_list(request: Request, form: schema.GetUserForm = Depends()):
    role_list = await Role.get_user_role_list(form.id)
    return request.app.get_success(role_list)


async def change_email(request: Request, form: schema.ChangeUserEmailForm):
    """ 修改用户邮箱 """
    await User.filter(id=form.id).update(email=form.email)
    return request.app.put_success()


async def reset_password(request: Request, form: schema.GetUserForm):
    user = await User.validate_is_exist("用户不存在", id=form.id)
    new_password = await user.reset_password(request.app.conf.password_secret_key)
    return request.app.success(f'重置成功，新密码为：{new_password}')


async def change_user_status(request: Request, form: schema.ChangeStatusUserForm):
    await User.filter(id=form.id).update(status=form.status)
    return request.app.put_success()


async def change_user_password(request: Request, form: schema.ChangePasswordForm):
    await form.validate_request()

    user = await User.filter(id=request.state.user.id).first()
    form.validate_is_true(user.verify_password(form.old_password, request.app.conf.password_secret_key), "账号或密码错误")

    new_password = User.password_to_hash(form.new_password, request.app.conf.password_secret_key)
    await User.filter(id=request.state.user.id).update(password=new_password)
    return request.app.put_success()


async def migrate_user_change_password(request: Request, form: schema.MigrateUserChangePasswordForm):
    await form.validate_request()
    user = await User.filter(id=request.state.user.id).first()
    form.validate_is_true(user.verify_password(form.old_password, request.app.conf.password_secret_key), "账号或密码错误")
    new_password = User.password_to_hash(form.new_password, request.app.conf.password_secret_key)
    await User.filter(id=user.id).update(password=new_password)
    return request.app.put_success()
