import validators
from typing import Optional, List
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm
from app.schemas.enums import DataStatusEnum

class FindUserForm(PaginationForm):
    """ 查找用户参数校验 """
    name: Optional[str] = Field(default=None, title="用户名")
    account: Optional[str] = Field(default=None, title="账号")
    detail: Optional[str] = Field(default=None, title="是否获取用户详情")
    status: Optional[DataStatusEnum] = Field(default=None, title="状态")
    role_id: Optional[int] = Field(default=None, title="角色id")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        user_id_list, filter_dict = kwargs.get("user_id_list"), {}

        if user_id_list:
            filter_dict["id__in"] = user_id_list
        if self.name:
            filter_dict["name__icontains"] = self.name
        if self.account:
            filter_dict["account"] = self.account
        if self.status:
            filter_dict["status"] = self.status
        if self.role_id:
            filter_dict["role_id"] = self.role_id
        return filter_dict


class UserForm(BaseForm):
    name: str = Field(..., title="用户名")
    account: str = Field(..., title="账号")
    password: str = Field(..., title="密码")
    email: Optional[str] = Field(default=None, title="邮箱")
    email_password: Optional[str] = Field(default=None, title="邮箱密码")
    role_list: List[int] = Field(..., title="角色")
    business_list: List[int] = Field(..., title="业务线")


class CreateUserForm(BaseForm):
    """ 创建用户的验证 """
    user_list: List[UserForm] = Field(..., title="要创建的用户列表")

    async def validate_request(self, *args, **kwargs):
        """ 校验用户数据 """
        user_list, name_list, account_list = [], [], []
        for index, user in enumerate(self.user_list):
            name, account, password = user.name, user.account, user.password
            business_list, role_list = user.business_list, user.role_list
            email = user.email
            if not all((name, account, password, business_list, role_list)):
                raise ValueError(f'第【{index + 1}】行，数据需填完')

            self.validate_is_true(3 < len(password) < 50, f'第【{index + 1}】行，密码长度长度为4~50位')

            if name in name_list:
                raise ValueError(f'第【{index + 1}】行，与第【{name_list.index(name) + 1}】行，用户名重复')
            self.validate_is_true(1 < len(name) < 12, f'第【{index + 1}】行，用户名长度长度为2~12位')

            if account in account_list:
                raise ValueError(f'第【{index + 1}】行，与第【{account_list.index(account) + 1}】行，账号重复')
            self.validate_is_true(1 < len(account) < 50, f'第【{index + 1}】行，账号长度长度为2~50位')

            if email and not validators.email(email.strip()):
                raise ValueError(f"第【{index + 1}】行，邮箱【{email}】格式错误")

            name_list.append(name)
            account_list.append(account)
            user_list.append(user)
        return user_list


class ChangePasswordForm(BaseForm):
    """ 修改密码的校验 """
    old_password: str = Field(..., title="旧密码", min_length=4)
    new_password: str = Field(..., title="新密码", min_length=4)
    sure_password: str = Field(..., title="确认密码", min_length=4)

    async def validate_request(self, *args, **kwargs):
        self.validate_is_true(self.new_password == self.sure_password, msg='新密码与确认密码不一致')


class MigrateUserChangePasswordForm(ChangePasswordForm):
    """ 迁移用户修改密码的校验，拿不到旧密码，所以不校验旧密码是否正确 """
    account: str = Field(..., title="账号")

class LoginForm(BaseForm):
    """ 登录校验 """
    account: str = Field(..., title="账号")
    password: str = Field(..., title="密码")


class GetUserForm(BaseForm):
    """ 获取用户信息 """
    id: int = Field(..., title="用户id")


class ChangeStatusUserForm(GetUserForm):
    """ 改变用户状态 """
    status: DataStatusEnum = Field(DataStatusEnum.ENABLE, title="状态")


class ChangeUserEmailForm(GetUserForm):
    email: str = Field(default=None, title="邮箱")


class EditUserForm(GetUserForm):
    """ 编辑用户的校验 """
    name: str = Field(..., title="用户名", min_length=2)
    account: str = Field(..., title="账号", min_length=2)
    business_list: list = Field(..., title="业务线")
    role_list: list = Field(..., title="角色")
    email: Optional[str] = Field(default=None, title="邮箱")
    email_password: Optional[str] = Field(default=None, title="邮箱密码")

    async def validate_request(self, *args, **kwargs):
        if self.email and not validators.email(self.email.strip()):
            raise ValueError(f"邮箱【{self.email}】格式错误")
