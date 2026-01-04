"""
需求管理和评审相关的Schema
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class RequirementDocumentBase(BaseModel):
    """需求文档基础Schema"""
    title: str = Field(..., description="文档标题")
    description: Optional[str] = Field(None, description="文档描述")
    document_type: str = Field(..., description="文档类型")
    content: Optional[str] = Field(None, description="文档内容")
    version: str = Field(default="1.0", description="版本号")


class RequirementDocumentCreate(RequirementDocumentBase):
    """创建需求文档Schema"""
    project_id: int = Field(..., description="项目ID")
    file_path: Optional[str] = Field(None, description="文件路径")


class RequirementDocumentUpdate(BaseModel):
    """更新需求文档Schema"""
    title: Optional[str] = Field(None, description="文档标题")
    description: Optional[str] = Field(None, description="文档描述")
    content: Optional[str] = Field(None, description="文档内容")
    status: Optional[str] = Field(None, description="状态")


class RequirementDocumentResponse(RequirementDocumentBase):
    """需求文档响应Schema"""
    id: UUID
    project_id: int
    status: str
    is_latest: bool
    uploader_id: Optional[int]
    uploaded_at: datetime
    updated_at: datetime
    word_count: int
    page_count: int

    class Config:
        from_attributes = True


class RequirementModuleBase(BaseModel):
    """需求模块基础Schema"""
    title: str = Field(..., description="模块名称")
    content: str = Field(..., description="模块内容")
    order: int = Field(default=0, description="排序")


class RequirementModuleCreate(RequirementModuleBase):
    """创建需求模块Schema"""
    document_id: UUID = Field(..., description="所属文档ID")
    parent_module_id: Optional[UUID] = Field(None, description="父模块ID")
    start_page: Optional[int] = Field(None, description="起始页码")
    end_page: Optional[int] = Field(None, description="结束页码")
    start_position: Optional[int] = Field(None, description="起始位置")
    end_position: Optional[int] = Field(None, description="结束位置")
    is_auto_generated: bool = Field(default=True, description="AI自动生成")
    confidence_score: Optional[float] = Field(None, description="置信度")
    ai_suggested_title: Optional[str] = Field(None, description="AI建议标题")


class RequirementModuleUpdate(BaseModel):
    """更新需求模块Schema"""
    title: Optional[str] = Field(None, description="模块名称")
    content: Optional[str] = Field(None, description="模块内容")
    order: Optional[int] = Field(None, description="排序")


class RequirementModuleResponse(RequirementModuleBase):
    """需求模块响应Schema"""
    id: UUID
    document_id: UUID
    parent_module_id: Optional[UUID]
    start_page: Optional[int]
    end_page: Optional[int]
    start_position: Optional[int]
    end_position: Optional[int]
    is_auto_generated: bool
    confidence_score: Optional[float]
    ai_suggested_title: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewReportBase(BaseModel):
    """评审报告基础Schema"""
    reviewer: str = Field(default="AI需求评审助手", description="评审人")
    review_type: str = Field(default="comprehensive", description="评审类型")


class ReviewReportCreate(ReviewReportBase):
    """创建评审报告Schema"""
    document_id: UUID = Field(..., description="评审文档ID")


class ReviewReportUpdate(BaseModel):
    """更新评审报告Schema"""
    status: Optional[str] = Field(None, description="评审状态")
    overall_rating: Optional[str] = Field(None, description="总体评价")
    completion_score: Optional[int] = Field(None, description="完整度评分")
    clarity_score: Optional[int] = Field(None, description="清晰度评分")
    consistency_score: Optional[int] = Field(None, description="一致性评分")
    completeness_score: Optional[int] = Field(None, description="完整性评分")
    testability_score: Optional[int] = Field(None, description="可测性评分")
    feasibility_score: Optional[int] = Field(None, description="可行性评分")
    total_issues: Optional[int] = Field(None, description="问题总数")
    high_priority_issues: Optional[int] = Field(None, description="高优先级问题")
    medium_priority_issues: Optional[int] = Field(None, description="中优先级问题")
    low_priority_issues: Optional[int] = Field(None, description="低优先级问题")
    summary: Optional[str] = Field(None, description="评审摘要")
    recommendations: Optional[str] = Field(None, description="改进建议")
    specialized_analyses: Optional[Dict[str, Any]] = Field(None, description="专项分析详情")


class ReviewReportResponse(ReviewReportBase):
    """评审报告响应Schema"""
    id: UUID
    document_id: UUID
    review_date: datetime
    status: str
    overall_rating: Optional[str]
    completion_score: int
    clarity_score: int
    consistency_score: int
    completeness_score: int
    testability_score: int
    feasibility_score: int
    total_issues: int
    high_priority_issues: int
    medium_priority_issues: int
    low_priority_issues: int
    summary: Optional[str]
    recommendations: Optional[str]
    specialized_analyses: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewIssueBase(BaseModel):
    """评审问题基础Schema"""
    issue_type: str = Field(..., description="问题类型")
    priority: str = Field(..., description="优先级")
    title: str = Field(..., description="问题标题")
    description: str = Field(..., description="问题描述")
    suggestion: Optional[str] = Field(None, description="改进建议")


class ReviewIssueCreate(ReviewIssueBase):
    """创建评审问题Schema"""
    report_id: UUID = Field(..., description="所属报告ID")
    module_id: Optional[UUID] = Field(None, description="相关模块ID")
    location: Optional[str] = Field(None, description="问题位置")
    page_number: Optional[int] = Field(None, description="页码")
    section: Optional[str] = Field(None, description="章节")


class ReviewIssueUpdate(BaseModel):
    """更新评审问题Schema"""
    title: Optional[str] = Field(None, description="问题标题")
    description: Optional[str] = Field(None, description="问题描述")
    suggestion: Optional[str] = Field(None, description="改进建议")
    is_resolved: Optional[bool] = Field(None, description="已解决")
    resolution_note: Optional[str] = Field(None, description="解决说明")


class ReviewIssueResponse(ReviewIssueBase):
    """评审问题响应Schema"""
    id: UUID
    report_id: UUID
    module_id: Optional[UUID]
    location: Optional[str]
    page_number: Optional[int]
    section: Optional[str]
    is_resolved: bool
    resolution_note: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModuleReviewResultBase(BaseModel):
    """模块评审结果基础Schema"""
    module_rating: Optional[str] = Field(None, description="模块评价")
    issues_count: int = Field(default=0, description="问题数量")
    severity_score: int = Field(default=0, description="严重程度评分")


class ModuleReviewResultCreate(ModuleReviewResultBase):
    """创建模块评审结果Schema"""
    report_id: UUID = Field(..., description="所属报告ID")
    module_id: UUID = Field(..., description="评审模块ID")
    analysis_content: Optional[str] = Field(None, description="分析内容")
    strengths: Optional[str] = Field(None, description="优点")
    weaknesses: Optional[str] = Field(None, description="不足")
    recommendations: Optional[str] = Field(None, description="改进建议")


class ModuleReviewResultUpdate(BaseModel):
    """更新模块评审结果Schema"""
    module_rating: Optional[str] = Field(None, description="模块评价")
    issues_count: Optional[int] = Field(None, description="问题数量")
    severity_score: Optional[int] = Field(None, description="严重程度评分")
    analysis_content: Optional[str] = Field(None, description="分析内容")
    strengths: Optional[str] = Field(None, description="优点")
    weaknesses: Optional[str] = Field(None, description="不足")
    recommendations: Optional[str] = Field(None, description="改进建议")


class ModuleReviewResultResponse(ModuleReviewResultBase):
    """模块评审结果响应Schema"""
    id: UUID
    report_id: UUID
    module_id: UUID
    analysis_content: Optional[str]
    strengths: Optional[str]
    weaknesses: Optional[str]
    recommendations: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RequirementBase(BaseModel):
    """需求基础Schema"""
    title: str = Field(..., description="需求标题")
    description: str = Field(..., description="需求描述")
    type: str = Field(..., description="需求类型")
    priority: str = Field(default="medium", description="优先级")
    status: str = Field(default="draft", description="状态")


class RequirementCreate(RequirementBase):
    """创建需求Schema"""
    stakeholders: List[str] = Field(default=[], description="相关人员列表")


class RequirementUpdate(BaseModel):
    """更新需求Schema"""
    title: Optional[str] = Field(None, description="需求标题")
    description: Optional[str] = Field(None, description="需求描述")
    type: Optional[str] = Field(None, description="需求类型")
    priority: Optional[str] = Field(None, description="优先级")
    status: Optional[str] = Field(None, description="状态")
    stakeholders: Optional[List[str]] = Field(None, description="相关人员列表")


class RequirementResponse(RequirementBase):
    """需求响应Schema"""
    id: UUID
    project_id: int
    stakeholders: List[str]
    creator_id: Optional[int]
    creator_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 批量操作Schema
class BatchModuleUpdateRequest(BaseModel):
    """批量更新模块请求Schema"""
    modules: List[RequirementModuleUpdate] = Field(..., description="模块列表")


class DocumentSplitRequest(BaseModel):
    """文档拆分请求Schema"""
    document_id: UUID = Field(..., description="文档ID")
    split_strategy: str = Field(default="auto", description="拆分策略")
    chunk_size: Optional[int] = Field(None, description="分块大小")


class ReviewRequest(BaseModel):
    """评审请求Schema"""
    document_id: UUID = Field(..., description="文档ID")
    review_type: str = Field(default="comprehensive", description="评审类型")
    focus_areas: Optional[List[str]] = Field(None, description="重点关注领域")


class ReviewProgressResponse(BaseModel):
    """评审进度响应Schema"""
    document_id: UUID
    status: str
    progress: float = Field(..., description="进度百分比")
    current_step: str = Field(..., description="当前步骤")
    estimated_time: Optional[int] = Field(None, description="预计剩余时间(秒)")


class RequirementSearchRequest(BaseModel):
    """需求搜索请求Schema"""
    keyword: Optional[str] = Field(None, description="关键词")
    type: Optional[str] = Field(None, description="需求类型")
    priority: Optional[str] = Field(None, description="优先级")
    status: Optional[str] = Field(None, description="状态")
    creator_id: Optional[int] = Field(None, description="创建人ID")
    page: int = Field(default=1, description="页码")
    page_size: int = Field(default=20, description="每页数量")


class RequirementStatistics(BaseModel):
    """需求统计Schema"""
    total_requirements: int = Field(..., description="需求总数")
    total_documents: int = Field(..., description="文档总数")
    total_modules: int = Field(..., description="模块总数")
    total_reviews: int = Field(..., description="评审总数")
    requirement_type_distribution: Dict[str, int] = Field(..., description="需求类型分布")
    requirement_priority_distribution: Dict[str, int] = Field(..., description="需求优先级分布")
    requirement_status_distribution: Dict[str, int] = Field(..., description="需求状态分布")
    document_status_distribution: Dict[str, int] = Field(..., description="文档状态分布")
    review_statistics: Dict[str, Any] = Field(..., description="评审统计信息")


class ProjectStatistics(BaseModel):
    """项目统计Schema"""
    total_knowledge_bases: int = Field(..., description="知识库总数")
    active_knowledge_bases: int = Field(..., description="活跃知识库数")
    inactive_knowledge_bases: int = Field(..., description="非活跃知识库数")
    total_documents: int = Field(..., description="文档总数")
    processed_documents: int = Field(..., description="已处理文档数")
    processing_documents: int = Field(..., description="处理中文档数")
    failed_documents: int = Field(..., description="失败文档数")
    total_requirements: int = Field(..., description="需求总数")
    requirement_type_distribution: Dict[str, int] = Field(..., description="需求类型分布")
    requirement_priority_distribution: Dict[str, int] = Field(..., description="需求优先级分布")
    total_chunks: int = Field(..., description="文档分块总数")
    system_status: str = Field(..., description="系统状态")
    database_status: str = Field(..., description="数据库状态")
    vector_db_status: str = Field(..., description="向量数据库状态")
    last_updated: str = Field(..., description="最后更新时间")


class RequirementDocumentDetail(RequirementDocumentResponse):
    """需求文档详情Schema"""
    modules: List[RequirementModuleResponse] = Field(default=[], description="模块列表")
    review_reports: List[ReviewReportResponse] = Field(default=[], description="评审报告列表")


class RequirementDocumentListResponse(BaseModel):
    """需求文档列表响应Schema"""
    items: List[RequirementDocumentResponse] = Field(..., description="文档列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class RequirementListResponse(BaseModel):
    """需求列表响应Schema"""
    items: List[RequirementResponse] = Field(..., description="需求列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class RequirementUploadRequest(BaseModel):
    """需求上传请求Schema"""
    project_id: int = Field(..., description="项目ID")
    title: str = Field(..., description="文档标题")
    description: Optional[str] = Field(None, description="文档描述")
    document_type: str = Field(..., description="文档类型")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小")
    file_content: Optional[str] = Field(None, description="文件内容")