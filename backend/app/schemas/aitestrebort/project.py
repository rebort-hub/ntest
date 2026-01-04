"""
aitestrebort 项目管理数据模式
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.base_form import PaginationForm


class aitestrebortProjectQueryForm(PaginationForm):
    """项目查询表单"""
    search: Optional[str] = Field(None, description="搜索关键词")
    
    def get_query_filter(self, *args, **kwargs):
        """查询条件"""
        filter_dict = {}
        if self.search:
            # 这里需要使用 Q 对象，但在 form 中我们先返回基本条件
            filter_dict["search"] = self.search
        return filter_dict


class aitestrebortProjectCredentialSchema(BaseModel):
    """项目凭据模式"""
    id: Optional[int] = None
    system_url: Optional[str] = Field(None, description="系统地址")
    username: Optional[str] = Field(None, description="用户名")
    password: Optional[str] = Field(None, description="密码")
    user_role: Optional[str] = Field(None, description="用户角色")
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class aitestrebortProjectMemberSchema(BaseModel):
    """项目成员模式"""
    id: Optional[int] = None
    user_id: int = Field(..., description="用户ID")
    role: str = Field("member", description="角色")
    joined_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class aitestrebortProjectSchema(BaseModel):
    """项目模式"""
    id: Optional[int] = None
    name: str = Field(..., max_length=255, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    creator_id: Optional[int] = Field(None, description="创建人ID")
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    
    # 关联数据
    credentials: Optional[List[aitestrebortProjectCredentialSchema]] = []
    members: Optional[List[aitestrebortProjectMemberSchema]] = []
    
    # 统计信息
    testcase_count: Optional[int] = 0
    member_count: Optional[int] = 0

    class Config:
        from_attributes = True


class aitestrebortProjectCreateSchema(BaseModel):
    """创建项目模式"""
    name: str = Field(..., max_length=255, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")


class aitestrebortProjectUpdateSchema(BaseModel):
    """更新项目模式"""
    name: Optional[str] = Field(None, max_length=255, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")


class aitestrebortProjectCredentialCreateSchema(BaseModel):
    """创建项目凭据模式"""
    system_url: Optional[str] = Field(None, description="系统地址")
    username: Optional[str] = Field(None, description="用户名")
    password: Optional[str] = Field(None, description="密码")
    user_role: Optional[str] = Field(None, description="用户角色")


class aitestrebortProjectMemberCreateSchema(BaseModel):
    """创建项目成员模式"""
    user_id: int = Field(..., description="用户ID")
    role: str = Field("member", description="角色")


class aitestrebortProjectListSchema(BaseModel):
    """项目列表模式"""
    id: int
    name: str
    description: Optional[str] = None
    creator_id: Optional[int] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    testcase_count: int = 0
    member_count: int = 0

    class Config:
        from_attributes = True


class aitestrebortProjectStatsSchema(BaseModel):
    """项目统计模式"""
    testcase_count: int = 0
    module_count: int = 0
    suite_count: int = 0
    member_count: int = 0
    execution_count: int = 0


class aitestrebortLLMConfigCreateSchema(BaseModel):
    """创建 LLM 配置模式"""
    name: str = Field(..., max_length=100, description="配置名称")
    config_name: Optional[str] = Field(None, max_length=255, description="用户自定义配置名称")
    provider: str = Field(..., description="提供商")
    model_name: str = Field(..., description="模型名称")
    api_key: str = Field(..., description="API 密钥")
    base_url: Optional[str] = Field(None, description="API 基础地址")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    temperature: Optional[float] = Field(0.7, description="温度参数")
    max_tokens: Optional[int] = Field(2000, description="最大令牌数")
    supports_vision: Optional[bool] = Field(False, description="是否支持视觉输入")
    context_limit: Optional[int] = Field(128000, description="上下文限制")
    is_default: Optional[bool] = Field(False, description="是否为默认配置")
    is_active: Optional[bool] = Field(True, description="是否启用")


class aitestrebortMCPConfigCreateSchema(BaseModel):
    """创建 MCP 配置模式 - 基于原Django架构"""
    name: str = Field(..., max_length=255, description="远程 MCP 服务器的名称")
    url: str = Field(..., max_length=2048, description="远程 MCP 服务器的 URL，例如 http://localhost:8765")
    transport: str = Field(default="streamable-http", description="传输协议：streamable-http, sse, stdio")
    headers: Optional[dict] = Field(default_factory=dict, description="认证头，例如 {'X-API-Key': 'your-key'}")
    is_enabled: Optional[bool] = Field(True, description="是否启用")


class aitestrebortAPIKeyCreateSchema(BaseModel):
    """创建 API 密钥模式"""
    name: str = Field(..., max_length=100, description="密钥名称")
    service_type: str = Field(..., description="服务类型")
    api_key: str = Field(..., description="API 密钥")
    description: Optional[str] = Field(None, description="描述")
    is_active: Optional[bool] = Field(True, description="是否激活")


class aitestrebortLLMConfigUpdateSchema(BaseModel):
    """更新 LLM 配置模式"""
    name: Optional[str] = Field(None, max_length=100, description="配置名称")
    config_name: Optional[str] = Field(None, max_length=255, description="用户自定义配置名称")
    provider: Optional[str] = Field(None, description="提供商")
    model_name: Optional[str] = Field(None, description="模型名称")
    api_key: Optional[str] = Field(None, description="API 密钥")
    base_url: Optional[str] = Field(None, description="API 基础地址")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    temperature: Optional[float] = Field(None, description="温度参数")
    max_tokens: Optional[int] = Field(None, description="最大令牌数")
    supports_vision: Optional[bool] = Field(None, description="是否支持视觉输入")
    context_limit: Optional[int] = Field(None, description="上下文限制")
    is_default: Optional[bool] = Field(None, description="是否为默认配置")
    is_active: Optional[bool] = Field(None, description="是否启用")


class aitestrebortMCPConfigUpdateSchema(BaseModel):
    """更新 MCP 配置模式 - 基于原Django架构"""
    name: Optional[str] = Field(None, max_length=255, description="远程 MCP 服务器的名称")
    url: Optional[str] = Field(None, max_length=2048, description="远程 MCP 服务器的 URL")
    transport: Optional[str] = Field(None, description="传输协议：streamable-http, sse, stdio")
    headers: Optional[dict] = Field(None, description="认证头")
    is_enabled: Optional[bool] = Field(None, description="是否启用")


class aitestrebortAPIKeyUpdateSchema(BaseModel):
    """更新 API 密钥模式"""
    name: Optional[str] = Field(None, max_length=100, description="密钥名称")
    service_type: Optional[str] = Field(None, description="服务类型")
    api_key: Optional[str] = Field(None, description="API 密钥")
    description: Optional[str] = Field(None, description="描述")
    is_active: Optional[bool] = Field(None, description="是否激活")


class aitestrebortConversationCreateSchema(BaseModel):
    """创建对话模式"""
    title: str = Field(..., max_length=200, description="对话标题")
    llm_config_id: Optional[int] = Field(None, description="LLM 配置ID")


class aitestrebortMessageCreateSchema(BaseModel):
    """创建消息模式"""
    content: str = Field(..., description="消息内容")
    role: Optional[str] = Field("user", description="角色")


class aitestrebortPromptCreateSchema(BaseModel):
    """创建提示词模式"""
    name: str = Field(..., max_length=255, description="提示词名称")
    content: str = Field(..., description="提示词内容")
    description: Optional[str] = Field(None, description="描述")
    prompt_type: str = Field(default='general', description="提示词类型")
    is_default: Optional[bool] = Field(False, description="是否为默认提示词")
    is_active: Optional[bool] = Field(True, description="是否启用")


class aitestrebortPromptUpdateSchema(BaseModel):
    """更新提示词模式"""
    name: Optional[str] = Field(None, max_length=255, description="提示词名称")
    content: Optional[str] = Field(None, description="提示词内容")
    description: Optional[str] = Field(None, description="描述")
    prompt_type: Optional[str] = Field(None, description="提示词类型")
    is_default: Optional[bool] = Field(None, description="是否为默认提示词")
    is_active: Optional[bool] = Field(None, description="是否启用")


class aitestrebortPromptSchema(BaseModel):
    """提示词模式"""
    id: int
    name: str
    content: str
    description: Optional[str] = None
    prompt_type: str
    is_default: bool
    is_active: bool
    user_id: int
    project_id: Optional[int] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True