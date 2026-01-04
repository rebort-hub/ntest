import httpx
from fastapi import Request, Depends

from ...models.system.model_factory import User, Role, UserRoles
from ...models.config.model_factory import BusinessLine
from ...schemas.system import sso as schema
from utils.parse.parse_token import parse_token


async def get_sso_server_info(request: Request):
    """ 获取sso相关信息 """
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(url=f'{request.app.conf._Sso.oss_host}/.well-known/openid-configuration', timeout=30)
    res = response.json()
    return {
        "authorization_endpoint": res["authorization_endpoint"], "token_endpoint": res["token_endpoint"],
        "userinfo_endpoint": res["userinfo_endpoint"], "jwks_uri": res["jwks_uri"]
    }


async def get_sso_token(request: Request, code):
    """ 从sso服务器获取用户token """
    sso_config = request.app.conf._Sso
    url = f'{sso_config.sso_host}{sso_config.sso_token_endpoint}'
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": sso_config.client_id,
        "client_secret": sso_config.client_secret,
        "redirect_uri": sso_config.redirect_uri
    }
    request.app.logger.info(f'get_sso_token: \nurl: {url}, \ndata: {data}')
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(url=url, data=data)
    request.app.logger.info(f'get_sso_token.res.text: \n{response.text}')
    return response.json()


async def get_sso_redirect_uri(request: Request):
    """ 返回重定向的登录地址 """
    redirect_addr = request.app.conf._Sso.front_redirect_addr if request.app.conf.auth_type == "SSO" else None
    return request.app.not_login(redirect_addr)



async def login_by_sso_code(request: Request, form: schema.GetSsoTokenForm = Depends()):

    # 根据接收到的code，获取token
    sso_token = await get_sso_token(request, form.code)

    # 解析token
    payload = parse_token(sso_token["id_token"])["payload"]
    sso_user_id, sso_user_name = payload.get("sub"), payload.get("user_name")
    phone_number, email = payload.get("phoneNumber"), payload.get("email")

    # user = User.query.filter_by(sso_user_id=sso_user_id, name=sso_user_name).first()
    user = await User.filter(sso_user_id=sso_user_id, name=sso_user_name).first()
    if not user:  # 数据库中没有这个用户，需插入一条数据，再生成token
        user = await User.filter(sso_user_id=None, name=sso_user_name).first()
        if user:
            await user.model_update({"sso_user_id": sso_user_id, "email": email, "phone_number": phone_number})
        else:
            # 新增用户，默认为公共业务线权限
            common_id = await BusinessLine.filter(code="common").first().values("id")
            user = await User.model_create({
                "sso_user_id": sso_user_id,
                "name": sso_user_name,
                "phone_number": phone_number,
                "email": email,
                "business_list": [common_id["id"]],
                "password": "123456"
            })

            # 角色为测试人员
            role_id = await Role.filter(name="测试人员").first().values("id")
            await UserRoles.model_create({"user_id": user.id, "role_id": role_id["id"]})
    else:  # 历史数据，如果没有手机号，需要更新一下
        if user.phone_number is None:
            await user.model_update({"email": email, "phone_number": phone_number})

    # 根据用户id信息生成token，并返回给前端
    user_info = await user.build_access_token(
        request.app.conf.access_token_time_out,
        request.app.conf.token_secret_key
    )
    user_info["refresh_token"] = user.make_refresh_token(
        request.app.conf.access_token_time_out,
        request.app.conf.token_secret_key
    )
    return request.app.success("登录成功", user_info)
