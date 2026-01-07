# -*- coding: utf-8 -*-
import os
import tempfile
from urllib.parse import urlparse
from fastapi import Request, HTTPException, Form
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils

from ...models.system.model_factory import User, Role, UserRoles
from ...models.config.model_factory import BusinessLine, SamlConfig
from ...schemas.system import saml as schema


def init_saml_auth(request: Request, saml_settings: dict):
    """初始化SAML认证对象"""
    req = prepare_fastapi_request(request)
    auth = OneLogin_Saml2_Auth(req, saml_settings)
    return auth


def prepare_fastapi_request(request: Request):
    """将FastAPI请求转换为python3-saml所需的格式"""
    url_data = urlparse(str(request.url))
    return {
        'https': 'on' if request.url.scheme == 'https' else 'off',
        'http_host': request.headers.get('host', url_data.netloc),
        'server_port': url_data.port or (443 if request.url.scheme == 'https' else 80),
        'script_name': request.url.path,
        'get_data': dict(request.query_params),
        'post_data': {}  # 将在具体使用时填充
    }


async def get_saml_config(config_id: int = None):
    """获取SAML配置"""
    if config_id:
        config = await SamlConfig.filter(id=config_id, status="enable").first()
    else:
        config = await SamlConfig.filter(is_default=True, status="enable").first()
    
    if not config:
        raise HTTPException(status_code=404, detail="未找到可用的SAML配置")
    
    return config


async def saml_login(request: Request, config_id: int = None):
    """发起SAML登录"""
    saml_config = await get_saml_config(config_id)
    saml_settings = await saml_config.get_saml_settings()
    
    auth = init_saml_auth(request, saml_settings)
    sso_url = auth.login()
    
    return {"redirect_url": sso_url}


async def saml_acs(request: Request, config_id: int = None):
    """处理SAML断言消费服务(ACS)"""
    saml_config = await get_saml_config(config_id)
    saml_settings = await saml_config.get_saml_settings()
    
    # 获取POST数据
    form_data = await request.form()
    req = prepare_fastapi_request(request)
    req['post_data'] = dict(form_data)
    
    auth = OneLogin_Saml2_Auth(req, saml_settings)
    auth.process_response()
    
    errors = auth.get_errors()
    if len(errors) == 0:
        # 认证成功，获取用户信息
        attributes = auth.get_attributes()
        name_id = auth.get_nameid()
        
        # 根据属性映射提取用户信息
        user_info = extract_user_info(attributes, saml_config.attribute_mapping, name_id)
        
        # 创建或更新用户
        user = await create_or_update_saml_user(user_info, request)
        
        # 生成访问令牌
        user_token_info = await user.build_access_token(
            request.app.conf.access_token_time_out,
            request.app.conf.token_secret_key
        )
        user_token_info["refresh_token"] = user.make_refresh_token(
            request.app.conf.refresh_token_time_out,
            request.app.conf.token_secret_key
        )
        
        return request.app.success("SAML登录成功", user_token_info)
    else:
        error_msg = f"SAML认证失败: {', '.join(errors)}"
        request.app.logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)


def extract_user_info(attributes: dict, attribute_mapping: dict, name_id: str):
    """从SAML属性中提取用户信息"""
    user_info = {"saml_name_id": name_id}
    
    for local_attr, saml_attr in attribute_mapping.items():
        if saml_attr in attributes and attributes[saml_attr]:
            # 取第一个值（SAML属性通常是数组）
            value = attributes[saml_attr][0] if isinstance(attributes[saml_attr], list) else attributes[saml_attr]
            user_info[local_attr] = value
    
    return user_info


async def create_or_update_saml_user(user_info: dict, request: Request):
    """创建或更新SAML用户"""
    saml_name_id = user_info.get("saml_name_id")
    username = user_info.get("username")
    email = user_info.get("email")
    
    # 首先尝试通过saml_name_id查找用户
    user = await User.filter(sso_user_id=saml_name_id).first()
    
    if not user and username:
        # 通过用户名查找
        user = await User.filter(name=username).first()
        if user:
            # 更新用户的SAML ID
            await user.model_update({"sso_user_id": saml_name_id})
    
    if not user:
        # 创建新用户
        # 获取默认业务线
        common_business = await BusinessLine.filter(code="common").first()
        business_list = [common_business.id] if common_business else []
        
        # 构建用户数据
        user_data = {
            "sso_user_id": saml_name_id,
            "name": username or email or saml_name_id,
            "email": email,
            "business_list": business_list,
            "password": "saml_user_no_password"  # SAML用户不需要密码
        }
        
        # 添加其他属性
        if user_info.get("first_name") and user_info.get("last_name"):
            user_data["name"] = f"{user_info['first_name']} {user_info['last_name']}"
        
        user = await User.model_create(user_data)
        
        # 分配默认角色（测试人员）
        default_role = await Role.filter(name="测试人员").first()
        if default_role:
            await UserRoles.model_create({"user_id": user.id, "role_id": default_role.id})
    else:
        # 更新现有用户信息
        update_data = {}
        if email and user.email != email:
            update_data["email"] = email
        
        if update_data:
            await user.model_update(update_data)
    
    return user


async def saml_logout(request: Request, config_id: int = None):
    """SAML单点登出"""
    saml_config = await get_saml_config(config_id)
    saml_settings = await saml_config.get_saml_settings()
    
    auth = init_saml_auth(request, saml_settings)
    slo_url = auth.logout()
    
    return {"redirect_url": slo_url}


async def saml_sls(request: Request, config_id: int = None):
    """处理SAML单点登出服务(SLS)"""
    saml_config = await get_saml_config(config_id)
    saml_settings = await saml_config.get_saml_settings()
    
    # 获取请求数据
    if request.method == "POST":
        form_data = await request.form()
        req = prepare_fastapi_request(request)
        req['post_data'] = dict(form_data)
    else:
        req = prepare_fastapi_request(request)
    
    auth = OneLogin_Saml2_Auth(req, saml_settings)
    url = auth.process_slo(delete_session_cb=lambda: None)
    
    errors = auth.get_errors()
    if len(errors) == 0:
        return {"message": "登出成功", "redirect_url": url}
    else:
        error_msg = f"SAML登出失败: {', '.join(errors)}"
        request.app.logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)


async def get_saml_metadata(request: Request, config_id: int = None):
    """获取SAML元数据"""
    try:
        saml_config = await get_saml_config(config_id)
        saml_settings = await saml_config.get_saml_settings()
        
        settings = OneLogin_Saml2_Settings(saml_settings)
        metadata = settings.get_sp_metadata()
        
        # 修复：check_sp_settings 是实例方法，需要通过实例调用
        errors = settings.check_sp_settings(saml_settings)
        
        if len(errors) == 0:
            return {
                "metadata": metadata,
                "content_type": "text/xml"
            }
        else:
            # 即使有警告也返回元数据，只记录日志
            request.app.logger.warning(f"SAML设置验证警告: {', '.join(errors)}")
            return {
                "metadata": metadata,
                "content_type": "text/xml"
            }
            
    except Exception as e:
        request.app.logger.error(f"获取SAML元数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取SAML元数据失败: {str(e)}")