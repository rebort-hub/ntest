"""
知识库管理数据模型
knowledge/models.py实现
"""
from tortoise import fields
from tortoise.models import Model


class aitestrebortKnowledgeBase(Model):
    """
    知识库模型，支持项目级别的知识库管理
    KnowledgeBase模型
    """
    
    id = fields.UUIDField(pk=True, description="知识库UUID")
    name = fields.CharField(max_length=200, description="知识库名称")
    description = fields.TextField(null=True, description="知识库描述")
    project = fields.ForeignKeyField(
        'test_platform.aitestrebortProject',
        related_name='knowledge_bases',
        on_delete=fields.CASCADE,
        description="所属项目"
    )
    creator = fields.ForeignKeyField(
        'test_platform.User',
        related_name='created_knowledge_bases',
        on_delete=fields.SET_NULL,
        null=True,
        description="创建者"
    )
    is_active = fields.BooleanField(default=True, description="是否启用")
    
    # 文档处理配置（可覆盖全局默认值）
    chunk_size = fields.IntField(default=1000, description="文本分块大小")
    chunk_overlap = fields.IntField(default=200, description="分块重叠大小")
    
    # 时间戳
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    
    class Meta:
        table = "aitestrebort_knowledge_base"
        ordering = ["-created_at"]
        unique_together = [("project", "name")]
    
    def __str__(self):
        return f"{self.name} (Project: {self.project_id})"


class aitestrebortDocument(Model):
    """
    文档模型，支持多种文档类型
    对应Document模型
    """
    
    DOCUMENT_TYPES = [
        ('pdf', 'PDF'),
        ('docx', 'Word文档'),
        ('pptx', 'PowerPoint'),
        ('txt', '文本文件'),
        ('md', 'Markdown'),
        ('html', 'HTML'),
        ('url', '网页链接'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '处理失败'),
    ]
    
    id = fields.UUIDField(pk=True, description="文档UUID")
    knowledge_base = fields.ForeignKeyField(
        'test_platform.aitestrebortKnowledgeBase',
        related_name='documents',
        on_delete=fields.CASCADE,
        description="所属知识库"
    )
    title = fields.CharField(max_length=200, description="文档标题")
    document_type = fields.CharField(max_length=10, description="文档类型")
    
    # 文件信息
    file_path = fields.CharField(max_length=1000, null=True, description="文件路径")
    url = fields.CharField(max_length=2000, null=True, description="网页链接")
    content = fields.TextField(null=True, description="文档内容")
    
    # 处理状态
    status = fields.CharField(max_length=20, default='pending', description="处理状态")
    error_message = fields.TextField(null=True, description="错误信息")
    
    # 元数据
    file_size = fields.IntField(null=True, description="文件大小(字节)")
    page_count = fields.IntField(null=True, description="页数")
    word_count = fields.IntField(null=True, description="字数")
    
    # 上传信息
    uploader = fields.ForeignKeyField(
        'test_platform.User',
        related_name='uploaded_documents',
        on_delete=fields.SET_NULL,
        null=True,
        description="上传者"
    )
    uploaded_at = fields.DatetimeField(auto_now_add=True, description="上传时间")
    processed_at = fields.DatetimeField(null=True, description="处理完成时间")
    
    class Meta:
        table = "aitestrebort_document"
        ordering = ["-uploaded_at"]
    
    def __str__(self):
        return f"{self.title} ({self.document_type})"


class aitestrebortDocumentChunk(Model):
    """
    文档分块模型，存储向量化后的文档片段
    对应DocumentChunk模型
    """
    
    id = fields.UUIDField(pk=True, description="分块UUID")
    document = fields.ForeignKeyField(
        'test_platform.aitestrebortDocument',
        related_name='chunks',
        on_delete=fields.CASCADE,
        description="所属文档"
    )
    chunk_index = fields.IntField(description="分块索引")
    content = fields.TextField(description="分块内容")
    
    # 向量存储相关
    vector_id = fields.CharField(max_length=100, null=True, description="向量ID")
    embedding_hash = fields.CharField(max_length=64, null=True, description="嵌入哈希")
    
    # 元数据
    start_index = fields.IntField(null=True, description="起始位置")
    end_index = fields.IntField(null=True, description="结束位置")
    page_number = fields.IntField(null=True, description="页码")
    
    # 时间戳
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    
    class Meta:
        table = "aitestrebort_document_chunk"
        ordering = ["document_id", "chunk_index"]
        unique_together = [("document", "chunk_index")]
    
    def __str__(self):
        return f"Chunk {self.chunk_index} of Document {self.document_id}"


class aitestrebortKnowledgeQuery(Model):
    """
    查询日志模型，记录知识库查询历史
    对应QueryLog模型
    """
    
    id = fields.UUIDField(pk=True, description="查询UUID")
    knowledge_base = fields.ForeignKeyField(
        'test_platform.aitestrebortKnowledgeBase',
        related_name='query_logs',
        on_delete=fields.CASCADE,
        description="所属知识库"
    )
    user = fields.ForeignKeyField(
        'test_platform.User',
        related_name='knowledge_queries',
        on_delete=fields.SET_NULL,
        null=True,
        description="查询用户"
    )
    
    # 查询信息
    query = fields.TextField(description="查询内容")
    response = fields.TextField(null=True, description="响应内容")
    
    # 检索结果
    retrieved_chunks = fields.JSONField(default=list, description="检索到的分块")
    similarity_scores = fields.JSONField(default=list, description="相似度分数")
    
    # 性能指标
    retrieval_time = fields.FloatField(null=True, description="检索耗时(秒)")
    generation_time = fields.FloatField(null=True, description="生成耗时(秒)")
    total_time = fields.FloatField(null=True, description="总耗时(秒)")
    
    # 时间戳
    created_at = fields.DatetimeField(auto_now_add=True, description="查询时间")
    
    class Meta:
        table = "aitestrebort_knowledge_query"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Query: {self.query[:50]}..."


class aitestrebortKnowledgeConfig(Model):
    """
    知识库全局配置模型，存储嵌入服务的默认配置
    采用单例模式，系统中只有一条配置记录
    对应KnowledgeGlobalConfig模型
    """
    
    EMBEDDING_SERVICE_CHOICES = [
        ('openai', 'OpenAI'),
        ('azure_openai', 'Azure OpenAI'),
        ('ollama', 'Ollama'),
        ('custom', '自定义API'),
    ]
    
    id = fields.IntField(pk=True, description="配置ID（固定为1，单例模式）")
    
    # 嵌入服务配置
    embedding_service = fields.CharField(
        max_length=50, 
        default='custom', 
        description="嵌入服务类型"
    )
    api_base_url = fields.CharField(
        max_length=500, 
        null=True, 
        description="API基础URL"
    )
    api_key = fields.CharField(
        max_length=500, 
        null=True, 
        description="API密钥"
    )
    model_name = fields.CharField(
        max_length=100, 
        default='text-embedding-ada-002', 
        description="模型名称"
    )
    
    # 默认分块配置
    chunk_size = fields.IntField(default=1000, description="默认分块大小")
    chunk_overlap = fields.IntField(default=200, description="默认分块重叠")
    
    # 更新信息
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    updated_by = fields.ForeignKeyField(
        'test_platform.User',
        related_name='updated_knowledge_configs',
        on_delete=fields.SET_NULL,
        null=True,
        description="更新人"
    )
    
    class Meta:
        table = "aitestrebort_knowledge_config"
    
    def __str__(self):
        return f"知识库全局配置 ({self.embedding_service})"
