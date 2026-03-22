"""
知识库管理 Schema
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class KnowledgeBaseCreate(BaseModel):
    """创建知识库请求"""
    name: str = Field(..., min_length=2, max_length=200, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    project_id: int = Field(..., description="所属项目ID")
    chunk_size: int = Field(1000, ge=100, le=2000, description="分块大小")
    chunk_overlap: int = Field(200, ge=0, le=500, description="分块重叠")
    is_active: bool = Field(True, description="是否启用")


class KnowledgeBaseUpdate(BaseModel):
    """更新知识库请求"""
    name: Optional[str] = Field(None, min_length=2, max_length=200, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    chunk_size: Optional[int] = Field(None, ge=100, le=2000, description="分块大小")
    chunk_overlap: Optional[int] = Field(None, ge=0, le=500, description="分块重叠")
    is_active: Optional[bool] = Field(None, description="是否启用")


class KnowledgeBaseResponse(BaseModel):
    """知识库响应"""
    id: UUID = Field(..., description="知识库ID")
    name: str = Field(..., description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    project_id: int = Field(..., description="所属项目ID")
    project_name: Optional[str] = Field(None, description="项目名称")
    creator_id: Optional[int] = Field(None, description="创建者ID")
    creator_name: Optional[str] = Field(None, description="创建者姓名")
    is_active: bool = Field(..., description="是否启用")
    chunk_size: int = Field(..., description="分块大小")
    chunk_overlap: int = Field(..., description="分块重叠")
    document_count: int = Field(0, description="文档数量")
    chunk_count: int = Field(0, description="分块数量")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class DocumentUpload(BaseModel):
    """文档上传请求"""
    title: str = Field(..., min_length=1, max_length=200, description="文档标题")
    document_type: str = Field(..., description="文档类型")
    url: Optional[str] = Field(None, description="网页链接")
    content: Optional[str] = Field(None, description="文档内容")
    
    @validator('document_type')
    def validate_document_type(cls, v):
        allowed_types = ['pdf', 'docx', 'pptx', 'txt', 'md', 'html', 'url']
        if v not in allowed_types:
            raise ValueError(f'文档类型必须是: {", ".join(allowed_types)}')
        return v
    
    @validator('url')
    def validate_url_for_type(cls, v, values):
        if values.get('document_type') == 'url' and not v:
            raise ValueError('网页链接类型必须提供URL')
        return v


class DocumentResponse(BaseModel):
    """文档响应"""
    id: UUID = Field(..., description="文档ID")
    knowledge_base_id: UUID = Field(..., description="所属知识库ID")
    knowledge_base_name: Optional[str] = Field(None, description="知识库名称")
    title: str = Field(..., description="文档标题")
    document_type: str = Field(..., description="文档类型")
    status: str = Field(..., description="处理状态")
    file_path: Optional[str] = Field(None, description="文件路径")
    url: Optional[str] = Field(None, description="网页链接")
    content: Optional[str] = Field(None, description="文档内容")
    file_size: Optional[int] = Field(None, description="文件大小")
    page_count: Optional[int] = Field(None, description="页数")
    word_count: Optional[int] = Field(None, description="字数")
    chunk_count: int = Field(0, description="分块数量")
    uploader_id: Optional[int] = Field(None, description="上传者ID")
    uploader_name: Optional[str] = Field(None, description="上传者姓名")
    error_message: Optional[str] = Field(None, description="错误信息")
    uploaded_at: datetime = Field(..., description="上传时间")
    processed_at: Optional[datetime] = Field(None, description="处理时间")


class DocumentChunkResponse(BaseModel):
    """文档分块响应"""
    id: UUID = Field(..., description="分块ID")
    document_id: UUID = Field(..., description="所属文档ID")
    document_title: Optional[str] = Field(None, description="文档标题")
    chunk_index: int = Field(..., description="分块索引")
    content: str = Field(..., description="分块内容")
    vector_id: Optional[str] = Field(None, description="向量ID")
    embedding_hash: Optional[str] = Field(None, description="嵌入哈希")
    start_index: Optional[int] = Field(None, description="起始位置")
    end_index: Optional[int] = Field(None, description="结束位置")
    page_number: Optional[int] = Field(None, description="页码")
    created_at: datetime = Field(..., description="创建时间")


class QueryRequest(BaseModel):
    """知识库查询请求"""
    query: str = Field(..., min_length=1, max_length=1000, description="查询内容")
    knowledge_base_id: UUID = Field(..., description="知识库ID")
    top_k: int = Field(5, ge=1, le=20, description="返回结果数量")
    similarity_threshold: float = Field(0.1, ge=0.0, le=1.0, description="相似度阈值")
    include_metadata: bool = Field(True, description="是否包含元数据")


class QuerySource(BaseModel):
    """查询结果来源"""
    content: str = Field(..., description="内容")
    similarity_score: float = Field(..., description="相似度分数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class QueryResponse(BaseModel):
    """知识库查询响应"""
    query: str = Field(..., description="查询内容")
    answer: Optional[str] = Field(None, description="生成的回答")
    sources: List[QuerySource] = Field(default_factory=list, description="检索来源")
    retrieval_time: float = Field(..., description="检索耗时(秒)")
    generation_time: Optional[float] = Field(None, description="生成耗时(秒)")
    total_time: float = Field(..., description="总耗时(秒)")


class QueryLogResponse(BaseModel):
    """查询日志响应"""
    id: UUID = Field(..., description="查询ID")
    knowledge_base_id: UUID = Field(..., description="知识库ID")
    knowledge_base_name: Optional[str] = Field(None, description="知识库名称")
    user_id: Optional[int] = Field(None, description="用户ID")
    user_name: Optional[str] = Field(None, description="用户姓名")
    query: str = Field(..., description="查询内容")
    response: Optional[str] = Field(None, description="响应内容")
    retrieved_chunks: List[Dict[str, Any]] = Field(default_factory=list, description="检索到的分块")
    similarity_scores: List[float] = Field(default_factory=list, description="相似度分数")
    retrieval_time: Optional[float] = Field(None, description="检索耗时(秒)")
    generation_time: Optional[float] = Field(None, description="生成耗时(秒)")
    total_time: Optional[float] = Field(None, description="总耗时(秒)")
    created_at: datetime = Field(..., description="查询时间")


# 系统状态Schema
class SystemStatus(BaseModel):
    """系统状态"""
    embedding_service: Dict[str, Any]
    vector_store: Dict[str, Any]
    dependencies: Dict[str, Any]


# 查询表单
class KnowledgeBaseQueryForm(BaseModel):
    """知识库查询表单"""
    project_id: Optional[int] = None
    search: Optional[str] = None
    is_active: Optional[bool] = None
    page: Optional[int] = 1
    page_size: Optional[int] = 20


class DocumentQueryForm(BaseModel):
    """文档查询表单"""
    search: Optional[str] = None
    status: Optional[str] = None
    page: Optional[int] = 1
    page_size: Optional[int] = 20
