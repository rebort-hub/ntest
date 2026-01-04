"""
aitestrebort 项目管理模型
基于 Tortoise ORM
"""
from tortoise.models import Model
from tortoise import fields
from ..base_model import BaseModel


class aitestrebortProject(BaseModel):
    """aitestrebort 项目模型"""
    
    name = fields.CharField(max_length=255, unique=True, description="项目名称")
    description = fields.TextField(null=True, description="项目描述")
    
    # 关联现有系统的用户
    creator_id = fields.IntField(description="创建人ID")
    
    class Meta:
        table = "aitestrebort_project"
        table_description = "aitestrebort 项目表"

    def __str__(self):
        return self.name


class aitestrebortProjectCredential(BaseModel):
    """项目凭据模型"""
    
    project = fields.ForeignKeyField(
        "test_platform.aitestrebortProject", 
        related_name="credentials",
        description="所属项目"
    )
    system_url = fields.CharField(max_length=500, null=True, description="系统地址")
    username = fields.CharField(max_length=100, null=True, description="用户名")
    password = fields.CharField(max_length=500, null=True, description="密码")
    user_role = fields.CharField(max_length=50, null=True, description="用户角色")
    
    class Meta:
        table = "aitestrebort_project_credential"
        table_description = "aitestrebort 项目凭据表"

    def __str__(self):
        return f"{self.project.name} - {self.user_role or self.username}"


class aitestrebortProjectMember(BaseModel):
    """项目成员模型"""
    
    project = fields.ForeignKeyField(
        "test_platform.aitestrebortProject",
        related_name="members",
        description="所属项目"
    )
    user_id = fields.IntField(description="用户ID")
    role = fields.CharField(
        max_length=20,
        default="tester",
        description="角色"
    )
    
    class Meta:
        table = "aitestrebort_project_member"
        table_description = "aitestrebort 项目成员表"
        unique_together = (("project", "user_id"),)

    def __str__(self):
        return f"{self.project.name} - User {self.user_id} ({self.role})"


class aitestrebortLLMConfig(BaseModel):
    """LLM 配置模型（支持全局配置和项目配置）"""
    
    project = fields.ForeignKeyField(
        "test_platform.aitestrebortProject",
        related_name="llm_configs",
        null=True,  # 允许为空，支持全局配置
        description="所属项目（为空时表示全局配置）"
    )
    
    # 配置标识字段（与原架构一致）
    config_name = fields.CharField(
        max_length=255, 
        null=True,
        description="用户自定义的配置名称，如'生产环境OpenAI'、'测试Claude配置'"
    )
    
    # 模型名称字段（原来的name字段，现在表示具体模型）
    name = fields.CharField(max_length=100, description="模型名称，如 gpt-4, claude-3-sonnet")
    provider = fields.CharField(max_length=50, description="LLM 提供商")  # openai, anthropic, etc.
    model_name = fields.CharField(max_length=100, description="模型名称（兼容字段）")
    api_key = fields.CharField(max_length=500, description="API 密钥")
    base_url = fields.CharField(max_length=500, null=True, description="API 基础URL")
    
    # 系统提示词（与原架构一致）
    system_prompt = fields.TextField(
        null=True,
        description="指导LLM行为的系统级提示词"
    )
    
    # 模型参数
    temperature = fields.FloatField(default=0.7, description="温度参数")
    max_tokens = fields.IntField(default=2000, description="最大令牌数")
    
    # 多模态支持（与原架构一致）
    supports_vision = fields.BooleanField(
        default=False,
        description="模型是否支持图片/多模态输入（如GPT-4V、Qwen-VL等）"
    )
    
    # 上下文限制（用于Token计数和对话压缩，与原架构一致）
    context_limit = fields.IntField(
        default=128000,
        description="模型最大上下文Token数（GPT-4o: 128000, Claude: 200000, Gemini: 1000000）"
    )
    
    # 状态字段
    is_default = fields.BooleanField(default=False, description="是否为默认配置")
    is_active = fields.BooleanField(default=True, description="是否启用")
    creator_id = fields.IntField(description="创建人ID")
    
    class Meta:
        table = "aitestrebort_llm_config"
        table_description = "aitestrebort LLM 配置表"

    def __str__(self):
        display_name = self.config_name or self.name
        if self.project_id:
            return f"{display_name} ({self.provider}) - 项目配置"
        return f"{display_name} ({self.provider}) - 全局配置"


class aitestrebortMCPConfig(BaseModel):
    """MCP 配置模型 - 完全对标RemoteMCPConfig"""
    
    # 移除project字段，只保留用户级配置
    user_id = fields.IntField(description="用户ID（配置拥有者）")
    name = fields.CharField(max_length=255, description="远程 MCP 服务器的名称")
    url = fields.CharField(max_length=2048, description="远程 MCP 服务器的 URL")
    transport = fields.CharField(
        max_length=50, 
        default="streamable-http", 
        description="MCP 服务器的传输协议，例如 'streamable-http'"
    )
    headers = fields.JSONField(default=dict, description="可选的认证头，例如 {'Authorization': 'Bearer YOUR_TOKEN'}")
    is_enabled = fields.BooleanField(default=True, description="是否启用此远程 MCP 服务器")
    creator_id = fields.IntField(description="创建人ID")
    
    # 保留旧字段以兼容现有数据（可选）
    command = fields.CharField(max_length=500, null=True, description="启动命令（已废弃）")
    args = fields.JSONField(default=list, description="命令参数（已废弃）")
    env = fields.JSONField(default=dict, description="环境变量（已废弃，使用headers）")
    working_dir = fields.CharField(max_length=500, null=True, description="工作目录（已废弃）")
    auto_start = fields.BooleanField(default=False, description="自动启动（已废弃）")
    timeout = fields.IntField(default=30, description="超时时间(秒)（已废弃）")
    
    class Meta:
        table = "aitestrebort_mcp_config"
        table_description = "aitestrebort MCP 配置表"

    def __str__(self):
        return f"用户{self.user_id} - {self.name}"


class aitestrebortAPIKey(BaseModel):
    """API 密钥管理模型 - 完全对标APIKey"""
    
    # 移除project字段，只保留用户级配置
    user_id = fields.IntField(description="用户ID（密钥拥有者）")
    name = fields.CharField(max_length=100, description="密钥名称")
    service = fields.CharField(max_length=50, description="服务类型")  # openai, anthropic, github, etc.
    key_value = fields.CharField(max_length=1000, description="密钥值")
    description = fields.TextField(null=True, description="描述")
    is_active = fields.BooleanField(default=True, description="是否启用")
    expires_at = fields.DatetimeField(null=True, description="过期时间")
    usage_count = fields.IntField(default=0, description="使用次数")
    last_used_at = fields.DatetimeField(null=True, description="最后使用时间")
    creator_id = fields.IntField(description="创建人ID")
    
    class Meta:
        table = "aitestrebort_api_key"
        table_description = "aitestrebort API 密钥表"

    def __str__(self):
        return f"用户{self.user_id} - {self.name} ({self.service})"


class aitestrebortConversation(BaseModel):
    """LLM 对话记录模型"""
    
    project = fields.ForeignKeyField(
        "test_platform.aitestrebortProject",
        related_name="conversations",
        description="所属项目"
    )
    session_id = fields.CharField(max_length=255, description="会话ID")
    title = fields.CharField(max_length=255, null=True, description="对话标题")
    llm_config = fields.ForeignKeyField(
        "test_platform.aitestrebortLLMConfig",
        related_name="conversations",
        null=True,
        description="使用的LLM配置"
    )
    prompt = fields.ForeignKeyField(
        "test_platform.aitestrebortPrompt",
        related_name="conversations",
        null=True,
        description="关联的提示词"
    )
    user_id = fields.IntField(description="用户ID")
    is_active = fields.BooleanField(default=True, description="是否活跃")
    
    class Meta:
        table = "aitestrebort_conversation"
        table_description = "aitestrebort 对话记录表"

    def __str__(self):
        return f"{self.project.name} - {self.title or self.session_id}"


class aitestrebortMessage(BaseModel):
    """对话消息模型"""
    
    conversation = fields.ForeignKeyField(
        "test_platform.aitestrebortConversation",
        related_name="messages",
        description="所属对话"
    )
    role = fields.CharField(max_length=20, description="角色")  # user, assistant, system
    content = fields.TextField(description="消息内容")
    message_type = fields.CharField(max_length=50, default="text", description="消息类型")
    metadata = fields.JSONField(default=dict, description="元数据")
    tokens_used = fields.IntField(null=True, description="使用的令牌数")
    
    class Meta:
        table = "aitestrebort_message"
        table_description = "aitestrebort 消息表"

    def __str__(self):
        return f"{self.conversation.session_id} - {self.role}: {self.content[:50]}..."


class aitestrebortPrompt(BaseModel):
    """提示词模型"""
    
    PROMPT_TYPE_CHOICES = [
        ('general', '通用对话'),
        ('completeness_analysis', '完整性分析'),
        ('consistency_analysis', '一致性分析'),
        ('testability_analysis', '可测性分析'),
        ('feasibility_analysis', '可行性分析'),
        ('clarity_analysis', '清晰度分析'),
        ('test_case_execution', '测试用例执行'),
        ('brain_orchestrator', '智能规划'),
        ('diagram_generation', '图表生成'),
    ]
    
    project = fields.ForeignKeyField(
        "test_platform.aitestrebortProject",
        related_name="prompts",
        null=True,
        description="所属项目（NULL表示全局提示词）"
    )
    user_id = fields.IntField(description="创建用户ID")
    name = fields.CharField(max_length=255, description="提示词名称")
    content = fields.TextField(description="提示词内容")
    description = fields.TextField(null=True, description="描述")
    prompt_type = fields.CharField(max_length=50, default='general', description="提示词类型")
    is_default = fields.BooleanField(default=False, description="是否为默认提示词")
    is_active = fields.BooleanField(default=True, description="是否启用")
    
    class Meta:
        table = "aitestrebort_prompt"
        table_description = "aitestrebort 提示词表"
        unique_together = (("user_id", "name", "project_id"),)

    def __str__(self):
        return f"{self.name} ({self.prompt_type})"