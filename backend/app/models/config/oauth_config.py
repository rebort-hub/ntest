from tortoise import fields
from ..base_model import BaseModel


class OAuthConfig(BaseModel):
    """OAuth 2.0配置模型"""
    
    name = fields.CharField(max_length=100, description="配置名称")
    provider = fields.CharField(max_length=50, description="OAuth提供商")
    client_id = fields.CharField(max_length=255, description="Client ID")
    client_secret = fields.CharField(max_length=255, description="Client Secret")
    authorize_url = fields.CharField(max_length=500, description="授权端点URL")
    token_url = fields.CharField(max_length=500, description="Token端点URL")
    user_info_url = fields.CharField(max_length=500, null=True, description="用户信息端点URL")
    redirect_uri = fields.CharField(max_length=500, description="回调地址")
    scope = fields.CharField(max_length=200, default="openid profile email", description="授权范围")
    status = fields.CharField(max_length=20, default="enabled", description="状态: enabled/disabled")
    is_default = fields.BooleanField(default=False, description="是否为默认配置")
    
    # 用户字段映射配置
    user_id_field = fields.CharField(max_length=50, default="id", description="用户ID字段")
    username_field = fields.CharField(max_length=50, default="name", description="用户名字段")
    email_field = fields.CharField(max_length=50, default="email", description="邮箱字段")
    avatar_field = fields.CharField(max_length=50, default="avatar_url", description="头像字段")
    
    description = fields.TextField(null=True, description="配置描述")
    
    class Meta:
        table = "oauth_config"
        table_description = "OAuth 2.0配置表"
        
    def __str__(self):
        return f"{self.name} ({self.provider})"