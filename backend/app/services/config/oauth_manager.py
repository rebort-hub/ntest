"""
OAuth配置管理器
统一管理UI配置和配置文件中的OAuth配置
"""
from typing import Optional, Dict, Any
from ...models.config.model_factory import OAuthConfig
from config import _Sso, auth_type


class OAuthConfigManager:
    """OAuth配置管理器"""
    
    @classmethod
    async def get_active_oauth_config(cls) -> Optional[Dict[str, Any]]:
        """
        获取当前激活的OAuth配置
        优先级：UI配置 > 配置文件配置
        """
        # 1. 首先尝试从UI配置中获取默认的启用配置
        ui_config = await cls._get_ui_default_config()
        if ui_config:
            return cls._convert_ui_config_to_dict(ui_config)
        
        # 2. 如果UI中没有配置，且配置文件中启用了SSO，则使用配置文件配置
        if auth_type == 'SSO':
            return cls._get_config_file_oauth()
        
        # 3. 都没有配置，返回None
        return None
    
    @classmethod
    async def get_oauth_login_url(cls) -> Optional[str]:
        """获取OAuth登录URL"""
        config = await cls.get_active_oauth_config()
        if not config:
            return None
        
        # 如果是配置文件中的配置，直接返回front_redirect_addr
        if config.get('source') == 'config_file':
            return _Sso.front_redirect_addr
        
        # 如果是UI配置，构建登录URL
        return cls._build_oauth_url(config)
    
    @classmethod
    async def _get_ui_default_config(cls) -> Optional[OAuthConfig]:
        """获取UI中的默认OAuth配置"""
        return await OAuthConfig.filter(
            status="enabled",
            is_default=True
        ).first()
    
    @classmethod
    def _get_config_file_oauth(cls) -> Dict[str, Any]:
        """获取配置文件中的OAuth配置"""
        return {
            'source': 'config_file',
            'name': 'Gitee SSO (配置文件)',
            'provider': 'gitee',
            'client_id': _Sso.client_id,
            'client_secret': _Sso.client_secret,
            'authorize_url': f"{_Sso.sso_host.rstrip('/')}{_Sso.sso_authorize_endpoint}",
            'token_url': f"{_Sso.sso_host.rstrip('/')}{_Sso.sso_token_endpoint}",
            'redirect_uri': _Sso.redirect_uri,
            'scope': 'openid',
            'user_id_field': 'id',
            'username_field': 'name',
            'email_field': 'email',
            'avatar_field': 'avatar_url'
        }
    
    @classmethod
    def _convert_ui_config_to_dict(cls, config: OAuthConfig) -> Dict[str, Any]:
        """将UI配置转换为字典格式"""
        return {
            'source': 'ui_config',
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
            'user_id_field': config.user_id_field,
            'username_field': config.username_field,
            'email_field': config.email_field,
            'avatar_field': config.avatar_field
        }
    
    @classmethod
    def _build_oauth_url(cls, config: Dict[str, Any]) -> str:
        """构建OAuth授权URL"""
        params = {
            'response_type': 'code',
            'client_id': config['client_id'],
            'redirect_uri': config['redirect_uri'],
            'scope': config['scope'],
            'state': 'oauth_login'  # 可以根据需要生成随机state
        }
        
        # 构建查询字符串
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{config['authorize_url']}?{query_string}"
    
    @classmethod
    async def migrate_config_file_to_ui(cls) -> Optional[OAuthConfig]:
        """
        将配置文件中的OAuth配置迁移到UI中
        如果UI中已经存在相同的配置，则不重复创建
        """
        if auth_type != 'SSO':
            return None
        
        # 检查是否已经存在相同的配置
        existing_config = await OAuthConfig.filter(
            provider='gitee',
            client_id=_Sso.client_id
        ).first()
        
        if existing_config:
            return existing_config
        
        # 创建新的UI配置
        config_data = {
            'name': 'Gitee SSO (从配置文件迁移)',
            'provider': 'gitee',
            'client_id': _Sso.client_id,
            'client_secret': _Sso.client_secret,
            'authorize_url': f"{_Sso.sso_host.rstrip('/')}{_Sso.sso_authorize_endpoint}",
            'token_url': f"{_Sso.sso_host.rstrip('/')}{_Sso.sso_token_endpoint}",
            'redirect_uri': _Sso.redirect_uri,
            'scope': 'openid',
            'status': 'enabled',
            'is_default': True,  # 设为默认配置
            'user_id_field': 'id',
            'username_field': 'name',
            'email_field': 'email',
            'avatar_field': 'avatar_url',
            'description': '从配置文件自动迁移的Gitee OAuth配置'
        }
        
        return await OAuthConfig.create(**config_data)
    
    @classmethod
    async def get_config_status(cls) -> Dict[str, Any]:
        """获取OAuth配置状态信息"""
        ui_configs = await OAuthConfig.filter(status="enabled").all()
        config_file_enabled = auth_type == 'SSO'
        
        active_config = await cls.get_active_oauth_config()
        
        return {
            'ui_configs_count': len(ui_configs),
            'config_file_enabled': config_file_enabled,
            'active_config_source': active_config.get('source') if active_config else None,
            'active_config_name': active_config.get('name') if active_config else None,
            'has_active_config': active_config is not None
        }