import httpx
from fastapi import Request, Depends
from tortoise.expressions import Q

from ...models.config.model_factory import OAuthConfig
from ...schemas.config import oauth_config as schema


def oauth_config_to_dict(config: OAuthConfig) -> dict:
    """将OAuth配置模型转换为字典"""
    return {
        'id': config.id,
        'name': config.name,
        'provider': config.provider,
        'client_id': config.client_id,
        'client_secret': config.client_secret,
        'authorize_url': config.authorize_url,
        'token_url': config.token_url,
        'user_info_url': config.user_info_url,
        'redirect_uri': config.redirect_uri,
        'scope': config.scope,
        'status': config.status,
        'is_default': config.is_default,
        'user_id_field': config.user_id_field,
        'username_field': config.username_field,
        'email_field': config.email_field,
        'avatar_field': config.avatar_field,
        'description': config.description,
        'created_at': config.create_time.isoformat() if config.create_time else None,
        'updated_at': config.update_time.isoformat() if config.update_time else None
    }


async def get_oauth_configs(request: Request, form: schema.OAuthConfigQueryForm = Depends()):
    """获取OAuth配置列表"""
    
    # 构建查询条件
    query = Q()
    if form.provider:
        query &= Q(provider=form.provider)
    if form.status:
        query &= Q(status=form.status)
    if form.name:
        query &= Q(name__icontains=form.name)
    
    # 计算偏移量
    page_no = form.page_no or 1
    page_size = form.page_size or 20
    offset = (page_no - 1) * page_size
    
    # 查询数据
    configs = await OAuthConfig.filter(query).order_by("-is_default", "-create_time").offset(offset).limit(page_size)
    total = await OAuthConfig.filter(query).count()
    
    # 转换为字典格式
    config_list = [oauth_config_to_dict(config) for config in configs]
    
    return request.app.get_success(data={
        "data": config_list,  # 改为 data 而不是 items
        "total": total,
        "page_no": page_no,
        "page_size": page_size
    }, msg="获取OAuth配置列表成功")


async def create_oauth_config(request: Request, form: schema.OAuthConfigForm):
    """创建OAuth配置"""
    
    # 检查配置名称是否已存在
    existing_config = await OAuthConfig.filter(name=form.name).first()
    if existing_config:
        return request.app.get_error(msg=f"配置名称 '{form.name}' 已存在")
    
    # 如果是第一个配置，自动设为默认
    config_count = await OAuthConfig.all().count()
    is_default = config_count == 0
    
    # 创建配置
    config_data = form.dict()
    config_data['is_default'] = is_default
    
    config = await OAuthConfig.create(**config_data)
    
    return request.app.get_success(
        data=oauth_config_to_dict(config),
        msg="OAuth配置创建成功"
    )


async def update_oauth_config(request: Request, config_id: int, form: schema.OAuthConfigUpdateForm):
    """更新OAuth配置"""
    
    config = await OAuthConfig.get_or_none(id=config_id)
    if not config:
        return request.app.get_error(msg="OAuth配置不存在")
    
    # 检查配置名称是否已存在（排除当前配置）
    if form.name:
        existing_config = await OAuthConfig.filter(name=form.name).exclude(id=config_id).first()
        if existing_config:
            return request.app.get_error(msg=f"配置名称 '{form.name}' 已存在")
    
    # 更新配置
    update_data = {k: v for k, v in form.dict().items() if v is not None}
    for key, value in update_data.items():
        setattr(config, key, value)
    await config.save()
    
    return request.app.get_success(
        data=oauth_config_to_dict(config),
        msg="OAuth配置更新成功"
    )


async def delete_oauth_config(request: Request, config_id: int):
    """删除OAuth配置"""
    
    config = await OAuthConfig.get_or_none(id=config_id)
    if not config:
        return request.app.get_error(msg="OAuth配置不存在")
    
    # 如果是默认配置，需要先设置其他配置为默认
    if config.is_default:
        other_config = await OAuthConfig.filter(id__not=config_id, status="enabled").first()
        if other_config:
            other_config.is_default = True
            await other_config.save()
    
    await config.delete()
    
    return request.app.get_success(msg="OAuth配置删除成功")


async def set_default_oauth_config(request: Request, form: schema.SetDefaultOAuthConfigForm):
    """设置默认OAuth配置"""
    
    config = await OAuthConfig.get_or_none(id=form.config_id)
    if not config:
        return request.app.get_error(msg="OAuth配置不存在")
    
    if config.status != "enabled":
        return request.app.get_error(msg="只能设置启用状态的配置为默认")
    
    # 取消其他配置的默认状态
    await OAuthConfig.all().update(is_default=False)
    
    # 设置当前配置为默认
    config.is_default = True
    await config.save()
    
    return request.app.get_success(msg="默认OAuth配置设置成功")


async def batch_delete_oauth_configs(request: Request, form: schema.BatchDeleteOAuthConfigForm):
    """批量删除OAuth配置"""
    
    configs = await OAuthConfig.filter(id__in=form.config_ids).all()
    if not configs:
        return request.app.get_error(msg="未找到要删除的OAuth配置")
    
    # 检查是否包含默认配置
    has_default = any(config.is_default for config in configs)
    
    # 删除配置
    await OAuthConfig.filter(id__in=form.config_ids).delete()
    
    # 如果删除了默认配置，设置其他配置为默认
    if has_default:
        remaining_config = await OAuthConfig.filter(status="enabled").first()
        if remaining_config:
            remaining_config.is_default = True
            await remaining_config.save()
    
    return request.app.get_success(msg=f"成功删除 {len(configs)} 个OAuth配置")


async def test_oauth_config(request: Request, config_id: int):
    """测试OAuth配置连接"""
    
    config = await OAuthConfig.get_or_none(id=config_id)
    if not config:
        return request.app.get_error(msg="OAuth配置不存在")
    
    try:
        # 测试授权端点连接
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 构建授权URL进行测试
            auth_params = {
                'response_type': 'code',
                'client_id': config.client_id,
                'redirect_uri': config.redirect_uri,
                'scope': config.scope,
                'state': 'test_connection'
            }
            
            # 测试授权端点
            auth_response = await client.get(config.authorize_url, params=auth_params)
            if auth_response.status_code not in [200, 302]:
                return request.app.get_error(msg=f"授权端点连接失败: HTTP {auth_response.status_code}")
            
            # 对于Token端点，我们只测试URL的可达性，不发送实际请求
            # 因为Token端点通常只接受POST请求且需要特定参数
            try:
                # 尝试连接到Token端点的域名和端口
                from urllib.parse import urlparse
                parsed_url = urlparse(config.token_url)
                test_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                
                # 测试基础连接
                base_response = await client.get(test_url, timeout=5.0)
                # 任何响应都表示服务器可达，包括404、403等
                if base_response.status_code >= 500:
                    return request.app.get_error(msg=f"Token端点服务器不可达: HTTP {base_response.status_code}")
            except Exception:
                return request.app.get_error(msg="Token端点服务器连接失败")
            
            # 如果有用户信息端点，也测试一下
            if config.user_info_url:
                user_info_response = await client.head(config.user_info_url)
                if user_info_response.status_code not in [200, 401, 405, 501]:  # 401表示需要认证但端点存在
                    return request.app.get_error(msg=f"用户信息端点连接失败: HTTP {user_info_response.status_code}")
        
        return request.app.get_success(msg="OAuth配置连接测试成功")
        
    except httpx.TimeoutException:
        return request.app.get_error(msg="连接超时，请检查网络或端点URL")
    except httpx.RequestError as e:
        return request.app.get_error(msg=f"连接失败: {str(e)}")
    except Exception as e:
        request.app.logger.error(f"OAuth配置测试失败: {str(e)}")
        return request.app.get_error(msg="连接测试失败，请检查配置")


async def test_oauth_connection(request: Request, form: schema.OAuthConfigTestForm):
    """测试OAuth连接（用于创建/编辑时的测试）"""
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 测试授权端点
            auth_params = {
                'response_type': 'code',
                'client_id': form.client_id,
                'scope': 'openid',
                'state': 'test_connection'
            }
            
            auth_response = await client.get(form.authorize_url, params=auth_params)
            if auth_response.status_code not in [200, 302]:
                return request.app.get_error(msg=f"授权端点连接失败: HTTP {auth_response.status_code}")
            
            # 对于Token端点，我们只测试URL的可达性
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(form.token_url)
                test_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                
                base_response = await client.get(test_url, timeout=5.0)
                if base_response.status_code >= 500:
                    return request.app.get_error(msg=f"Token端点服务器不可达: HTTP {base_response.status_code}")
            except Exception:
                return request.app.get_error(msg="Token端点服务器连接失败")
            
            # 测试用户信息端点
            if form.user_info_url:
                user_info_response = await client.head(form.user_info_url)
                if user_info_response.status_code not in [200, 401, 405, 501]:
                    return request.app.get_error(msg=f"用户信息端点连接失败: HTTP {user_info_response.status_code}")
        
        return request.app.get_success(msg="OAuth连接测试成功")
        
    except httpx.TimeoutException:
        return request.app.get_error(msg="连接超时，请检查网络或端点URL")
    except httpx.RequestError as e:
        return request.app.get_error(msg=f"连接失败: {str(e)}")
    except Exception as e:
        request.app.logger.error(f"OAuth连接测试失败: {str(e)}")
        return request.app.get_error(msg="连接测试失败，请检查配置")


async def get_oauth_providers(request: Request):
    """获取支持的OAuth提供商列表"""
    
    providers = [
        {
            "value": "github",
            "label": "GitHub",
            "icon": "github",
            "color": "#24292e",
            "preset": {
                "authorize_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "user_info_url": "https://api.github.com/user",
                "scope": "user:email",
                "user_id_field": "id",
                "username_field": "login",
                "email_field": "email",
                "avatar_field": "avatar_url"
            }
        },
        {
            "value": "gitee",
            "label": "Gitee",
            "icon": "gitee",
            "color": "#c71d23",
            "preset": {
                "authorize_url": "https://gitee.com/oauth/authorize",
                "token_url": "https://gitee.com/oauth/token",
                "user_info_url": "https://gitee.com/api/v5/user",
                "scope": "user_info",
                "user_id_field": "id",
                "username_field": "name",
                "email_field": "email",
                "avatar_field": "avatar_url"
            }
        },
        {
            "value": "google",
            "label": "Google",
            "icon": "google",
            "color": "#4285f4",
            "preset": {
                "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "scope": "openid profile email",
                "user_id_field": "id",
                "username_field": "name",
                "email_field": "email",
                "avatar_field": "picture"
            }
        },
        {
            "value": "microsoft",
            "label": "Microsoft",
            "icon": "microsoft",
            "color": "#00a1f1",
            "preset": {
                "authorize_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
                "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                "user_info_url": "https://graph.microsoft.com/v1.0/me",
                "scope": "openid profile email",
                "user_id_field": "id",
                "username_field": "displayName",
                "email_field": "mail",
                "avatar_field": "photo"
            }
        },
        {
            "value": "wechat",
            "label": "微信",
            "icon": "wechat",
            "color": "#07c160",
            "preset": {
                "authorize_url": "https://open.weixin.qq.com/connect/oauth2/authorize",
                "token_url": "https://api.weixin.qq.com/sns/oauth2/access_token",
                "user_info_url": "https://api.weixin.qq.com/sns/userinfo",
                "scope": "snsapi_userinfo",
                "user_id_field": "openid",
                "username_field": "nickname",
                "email_field": "email",
                "avatar_field": "headimgurl"
            }
        },
        {
            "value": "custom",
            "label": "自定义",
            "icon": "custom",
            "color": "#909399",
            "preset": {
                "authorize_url": "",
                "token_url": "",
                "user_info_url": "",
                "scope": "openid profile email",
                "user_id_field": "id",
                "username_field": "name",
                "email_field": "email",
                "avatar_field": "avatar_url"
            }
        }
    ]
    
    return request.app.get_success(data=providers)


async def get_oauth_config_status(request: Request):
    """获取OAuth配置状态"""
    from .oauth_manager import OAuthConfigManager
    
    status = await OAuthConfigManager.get_config_status()
    return request.app.get_success(data=status)


async def migrate_config_file_oauth(request: Request):
    """将配置文件中的OAuth配置迁移到UI中"""
    from .oauth_manager import OAuthConfigManager
    
    config = await OAuthConfigManager.migrate_config_file_to_ui()
    if config:
        return request.app.get_success(
            data=oauth_config_to_dict(config),
            msg="配置文件OAuth配置迁移成功"
        )
    else:
        return request.app.get_error(msg="无需迁移或迁移失败")


async def get_active_oauth_config(request: Request):
    """获取当前激活的OAuth配置"""
    from .oauth_manager import OAuthConfigManager
    
    config = await OAuthConfigManager.get_active_oauth_config()
    if config:
        return request.app.get_success(data=config)
    else:
        return request.app.get_error(msg="未找到激活的OAuth配置")