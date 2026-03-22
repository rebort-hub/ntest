from ..base_view import APIRouter
from ...services.system import user as user_service

user_router = APIRouter()


user_router.add_get_route("/list", user_service.get_user_list, summary="获取用户列表")
user_router.add_put_route("/sort", user_service.change_user_sort, summary="修改用户排序")
user_router.add_get_route("/role", user_service.get_user_role_list, summary="获取用户的角色列表")
user_router.add_post_route("/login", user_service.user_login, auth=False, summary="用户登录")
user_router.add_get_route("/refresh", user_service.refresh_token, auth=False, summary="刷新token")
user_router.add_post_route("/logout", user_service.user_logout, summary="用户登出")
user_router.add_put_route("/password", user_service.change_user_password, summary="修改密码")
user_router.add_put_route("/email", user_service.change_email, summary="修改用户邮箱")
user_router.add_put_route("/reset-password", user_service.reset_password, summary="重置密码")
user_router.add_put_route("/status", user_service.change_user_status, summary="修改用户状态")
user_router.add_get_route("", user_service.get_user_detail, summary="获取用户详情")
user_router.add_post_route("", user_service.add_user, summary="新增用户")
user_router.add_put_route("", user_service.change_user, summary="修改用户")
user_router.add_delete_route("", user_service.delete_user, summary="删除用户")
user_router.add_put_route("/password/migrate", user_service.migrate_user_change_password, summary="迁移用户修改密码")
