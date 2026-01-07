from typing import Optional
from pydantic import Field, validator

from ..base_form import BaseForm, PaginationForm


class OAuthConfigForm(BaseForm):
    """OAuth配置表单"""
    name: str = Field(..., title="配置名称", min_length=2, max_length=100)
    provider: str = Field(..., title="OAuth提供商")
    client_id: str = Field(..., title="Client ID")
    client_secret: str = Field(..., title="Client Secret")
    authorize_url: str = Field(..., title="授权端点URL")
    token_url: str = Field(..., title="Token端点URL")
    user_info_url: Optional[str] = Field(None, title="用户信息端点URL")
    redirect_uri: str = Field(..., title="回调地址")
    scope: str = Field(default="openid profile email", title="授权范围")
    status: str = Field(default="enabled", title="状态")
    user_id_field: str = Field(default="id", title="用户ID字段")
    username_field: str = Field(default="name", title="用户名字段")
    email_field: str = Field(default="email", title="邮箱字段")
    avatar_field: str = Field(default="avatar_url", title="头像字段")
    description: Optional[str] = Field(None, title="配置描述")
    
    @validator('status')
    def validate_status(cls, v):
        if v not in ['enabled', 'disabled']:
            raise ValueError('状态必须是 enabled 或 disabled')
        return v
    
    @validator('provider')
    def validate_provider(cls, v):
        allowed_providers = [
            'github', 'gitee', 'google', 'microsoft', 
            'wechat', 'qq', 'dingtalk', 'feishu', 'custom'
        ]
        if v not in allowed_providers:
            raise ValueError(f'不支持的OAuth提供商: {v}')
        return v


class OAuthConfigUpdateForm(BaseForm):
    """OAuth配置更新表单"""
    name: Optional[str] = Field(None, title="配置名称", min_length=2, max_length=100)
    provider: Optional[str] = Field(None, title="OAuth提供商")
    client_id: Optional[str] = Field(None, title="Client ID")
    client_secret: Optional[str] = Field(None, title="Client Secret")
    authorize_url: Optional[str] = Field(None, title="授权端点URL")
    token_url: Optional[str] = Field(None, title="Token端点URL")
    user_info_url: Optional[str] = Field(None, title="用户信息端点URL")
    redirect_uri: Optional[str] = Field(None, title="回调地址")
    scope: Optional[str] = Field(None, title="授权范围")
    status: Optional[str] = Field(None, title="状态")
    user_id_field: Optional[str] = Field(None, title="用户ID字段")
    username_field: Optional[str] = Field(None, title="用户名字段")
    email_field: Optional[str] = Field(None, title="邮箱字段")
    avatar_field: Optional[str] = Field(None, title="头像字段")
    description: Optional[str] = Field(None, title="配置描述")
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None and v not in ['enabled', 'disabled']:
            raise ValueError('状态必须是 enabled 或 disabled')
        return v


class OAuthConfigQueryForm(PaginationForm):
    """OAuth配置查询表单"""
    provider: Optional[str] = Field(None, title="OAuth提供商")
    status: Optional[str] = Field(None, title="状态")
    name: Optional[str] = Field(None, title="配置名称")


class OAuthConfigTestForm(BaseForm):
    """OAuth配置测试表单"""
    client_id: str = Field(..., title="Client ID")
    client_secret: str = Field(..., title="Client Secret")
    authorize_url: str = Field(..., title="授权端点URL")
    token_url: str = Field(..., title="Token端点URL")
    user_info_url: Optional[str] = Field(None, title="用户信息端点URL")


class SetDefaultOAuthConfigForm(BaseForm):
    """设置默认OAuth配置表单"""
    config_id: int = Field(..., title="配置ID")


class BatchDeleteOAuthConfigForm(BaseForm):
    """批量删除OAuth配置表单"""
    config_ids: list[int] = Field(..., title="配置ID列表")