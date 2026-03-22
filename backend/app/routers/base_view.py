from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI as _FastAPI,APIRouter as fastAPIRouter,   Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from ..schemas.base_form import CurrentUserModel


async def get_current_user(request: Request) -> CurrentUserModel:
    """获取当前用户信息"""
    if hasattr(request.state, 'user'):
        return request.state.user
    else:
        # 如果没有用户信息，返回一个空的用户模型
        return CurrentUserModel()


class FastAPI(_FastAPI):
    """ 重写fastapi """
    request_id = None  # 记录request_id，方便跟踪链路查问题
    request_path = None  # 请求地址

    def restful_result(self, code, message, data, **kwargs):
        response_content = jsonable_encoder({"status": code, "message": message, "data": data, **kwargs})
        return JSONResponse(status_code=200 if code != 500 else 500, content=response_content)

    def success(self, msg=None, data=None, **kwargs):
        """ 业务处理成功的响应 """
        return self.restful_result(code=200, message=msg or "处理成功", data=data, **kwargs)

    def trigger_success(self, data=None, msg=None, **kwargs):
        """ 触发运行成功的响应 """
        return self.success(msg=msg or "触发执行成功，请等待执行完毕", data=data, **kwargs)

    def get_success(self, data=None, msg=None, **kwargs):
        """ 数据获取成功的响应 """
        return self.success(msg=msg or "获取成功", data=data, **kwargs)

    def get_error(self, data=None, msg=None, **kwargs):
        """ 数据获取失败的响应 """
        return self.fail(msg=msg or "获取失败", data=data, **kwargs)

    def post_success(self, data=None, msg=None, **kwargs):
        """ 数据新增成功的响应 """
        return self.success(msg=msg or "新增成功", data=data, **kwargs)

    def put_success(self, data=None, msg=None, **kwargs):
        """ 数据修改成功的响应 """
        return self.success(msg=msg or "修改成功", data=data, **kwargs)

    def delete_success(self, data=None, msg=None, **kwargs):
        """ 数据删除成功的响应 """
        return self.success(msg=msg or "删除成功", data=data, **kwargs)

    def fail(self, msg=None, data=None, **kwargs):
        """ 业务处理失败的响应 """
        return self.restful_result(code=400, message=msg or "处理失败", data=data, **kwargs)

    def not_login(self, msg=None, data=None, **kwargs):
        """ 未登录的响应 """
        return self.restful_result(code=401, message=msg or "请重新登录", data=data, **kwargs)

    def forbidden(self, msg=None, data=None, **kwargs):
        """ 权限不足 """
        return self.restful_result(code=403, message=msg or "权限不足", data=data, **kwargs)

    def need_reset_password(self, msg=None, data=None, **kwargs):
        """ 需要重置密码 """
        return self.restful_result(code=4003, message=msg or "请重置密码", data=data, **kwargs)

    def url_not_find(self, msg=None, data=None, **kwargs):
        """ url不存在 """
        return self.restful_result(code=404, message=msg or "url不存在", data=data, **kwargs)

    def method_not_allowed(self, msg=None, data=None, **kwargs):
        """ 请求方法错误 """
        return self.restful_result(code=405, message=msg or "请求方法错误", data=data, **kwargs)

    def error(self, msg=None, data=None, **kwargs):
        """ 系统发送错误的响应 """
        return self.restful_result(code=500, message=msg or "系统出错了，请联系开发人员查看", data=data, **kwargs)


class SuccessModel(BaseModel):
    status: int = 200
    message: str = "操作成功"
    data: dict = {}


class APIRouter(fastAPIRouter):

    def __init__(self, *args, **kwargs):
        super(APIRouter, self).__init__(*args, **kwargs)

    @classmethod
    def request_path_is_in_whitelist(cls, request: Request) -> bool:
        """ 访问以下接口不用校验身份 """
        return request.url.path in [
            request.app.docs_url,
            request.app.redoc_url,
            "/docs",
            "/redoc",
            request.app.openapi_url
        ]

    @classmethod
    async def check_login(cls, request: Request):
        """ 判断是否登录 """
        if cls.request_path_is_in_whitelist(request) is False:
            from app.models.system.model_factory import User
            if user := User.check_token(request.headers.get("access-token", ""), request.app.conf.token_secret_key):
                request.state.user = CurrentUserModel(**user)
            else:
                raise HTTPException(401, "请重新登录")

    @classmethod
    async def check_api_permission(cls, request: Request):
        """ 判断是否有api权限 """
        await cls.check_login(request)
        if "admin" not in request.state.user.api_permissions and request.url.path not in request.state.user.api_permissions:
            raise HTTPException(403, "权限不足")

    def add_route(self, path, func, methods: list, auth: Union[str, bool], *args, **kwargs):
        if auth:
            if auth == 'login':  # 只验证登录
                kwargs.setdefault('dependencies', []).append(Depends(self.check_login))
            if auth == 'api':  # 验证接口权限
                kwargs.setdefault('dependencies', []).append(Depends(self.check_api_permission))
        if kwargs.get("response_model", None) is None:  # 自动加响应模型
            kwargs["response_model"] = SuccessModel
        return self.add_api_route(path, func, methods=methods, *args, **kwargs)

    def add_get_route(self, path, func, auth: Union[str, bool] = 'login', *args, **kwargs):
        return self.add_route(path, func, methods=["GET"], auth=auth, *args, **kwargs)

    def add_post_route(self, path, func, auth: Union[str, bool] = 'login', *args, **kwargs):
        return self.add_route(path, func, methods=["POST"], auth=auth, *args, **kwargs)

    def add_put_route(self, path, func, auth: Union[str, bool] = 'login', *args, **kwargs):
        return self.add_route(path, func, methods=["PUT"], auth=auth, *args, **kwargs)

    def add_delete_route(self, path, func, auth: Union[str, bool] = 'login', *args, **kwargs):
        return self.add_route(path, func, methods=["DELETE"], auth=auth, *args, **kwargs)
