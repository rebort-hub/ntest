"""
需求管理模型
使用Tortoise ORM
"""
from tortoise.models import Model
from tortoise import fields
from enum import Enum


class RequirementType(str, Enum):
    """需求类型枚举"""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non-functional"
    BUSINESS = "business"
    USER = "user"
    SYSTEM = "system"


class RequirementPriority(str, Enum):
    """需求优先级枚举"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RequirementStatus(str, Enum):
    """需求状态枚举"""
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class DocumentType(str, Enum):
    """文档类型枚举"""
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    TXT = "txt"
    MD = "md"
    HTML = "html"


class DocumentStatus(str, Enum):
    """文档状态枚举"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    MODULE_SPLIT = "module_split"
    USER_REVIEWING = "user_reviewing"
    READY_FOR_REVIEW = "ready_for_review"
    REVIEWING = "reviewing"
    REVIEW_COMPLETED = "review_completed"
    FAILED = "failed"


class RequirementDocument(Model):
    """需求文档模型"""
    id = fields.CharField(max_length=36, pk=True)
    project_id = fields.IntField(description="项目ID")
    title = fields.CharField(max_length=200, description="文档标题")
    description = fields.TextField(null=True, description="文档描述")
    document_type = fields.CharField(max_length=50, description="文档类型")
    file_path = fields.CharField(max_length=500, null=True, description="文件路径")
    content = fields.TextField(null=True, description="文档内容")
    
    # 状态管理
    status = fields.CharField(max_length=20, default="uploaded", description="状态")
    
    # 版本管理
    version = fields.CharField(max_length=20, default="1.0", description="版本号")
    is_latest = fields.BooleanField(default=True, description="是否最新版本")
    parent_document_id = fields.CharField(max_length=36, null=True, description="父文档ID")
    
    # 元数据
    uploader_id = fields.IntField(null=True, description="上传人ID")
    uploaded_at = fields.DatetimeField(auto_now_add=True, description="上传时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    
    # 统计信息
    word_count = fields.IntField(default=0, description="字数")
    page_count = fields.IntField(default=0, description="页数")

    class Meta:
        table = "requirement_documents"
        table_description = "需求文档表"


class RequirementModule(Model):
    """需求模块模型"""
    id = fields.CharField(max_length=36, pk=True)
    document = fields.ForeignKeyField(
        'test_platform.RequirementDocument',
        related_name='modules',
        description="所属文档"
    )
    title = fields.CharField(max_length=200, description="模块名称")
    content = fields.TextField(description="模块内容")
    
    # 位置信息
    start_page = fields.IntField(null=True, description="起始页码")
    end_page = fields.IntField(null=True, description="结束页码")
    start_position = fields.IntField(null=True, description="起始位置")
    end_position = fields.IntField(null=True, description="结束位置")
    
    # 排序和分组
    order_num = fields.IntField(default=0, description="排序", db_column="order_num")
    parent_module_id = fields.CharField(max_length=36, null=True, description="父模块ID")
    
    # AI分析信息
    is_auto_generated = fields.BooleanField(default=True, description="AI自动生成")
    confidence_score = fields.FloatField(null=True, description="置信度")
    ai_suggested_title = fields.CharField(max_length=200, null=True, description="AI建议标题")
    
    # 元数据
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "requirement_modules"
        table_description = "需求模块表"


class Requirement(Model):
    """需求模型 - 手动创建的需求"""
    id = fields.CharField(max_length=36, pk=True)
    project_id = fields.IntField(description="项目ID")
    title = fields.CharField(max_length=200, description="需求标题")
    description = fields.TextField(description="需求描述")
    
    # 需求分类
    type = fields.CharField(max_length=20, description="需求类型")
    priority = fields.CharField(max_length=10, default="medium", description="优先级")
    status = fields.CharField(max_length=20, default="draft", description="状态")
    
    # 相关人员 (JSON字段)
    stakeholders = fields.JSONField(default=list, description="相关人员列表")
    
    # 元数据
    creator_id = fields.IntField(null=True, description="创建人ID")
    creator_name = fields.CharField(max_length=100, null=True, description="创建人姓名")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "requirements"
        table_description = "需求表"


class ReviewReport(Model):
    """评审报告模型"""
    id = fields.CharField(max_length=36, pk=True)
    document_id = fields.CharField(max_length=36, description="评审文档ID")
    
    # 评审基本信息
    review_date = fields.DatetimeField(auto_now_add=True, description="评审时间")
    reviewer = fields.CharField(max_length=100, default="AI需求评审助手", description="评审人")
    review_type = fields.CharField(max_length=20, default="comprehensive", description="评审类型")
    status = fields.CharField(max_length=20, default="pending", description="评审状态")
    
    # 评审结果
    overall_rating = fields.CharField(max_length=20, null=True, description="总体评价")
    completion_score = fields.IntField(default=0, description="完整度评分")
    clarity_score = fields.IntField(default=0, description="清晰度评分")
    consistency_score = fields.IntField(default=0, description="一致性评分")
    completeness_score = fields.IntField(default=0, description="完整性评分")
    testability_score = fields.IntField(default=0, description="可测性评分")
    feasibility_score = fields.IntField(default=0, description="可行性评分")
    
    # 问题统计
    total_issues = fields.IntField(default=0, description="问题总数")
    high_priority_issues = fields.IntField(default=0, description="高优先级问题")
    medium_priority_issues = fields.IntField(default=0, description="中优先级问题")
    low_priority_issues = fields.IntField(default=0, description="低优先级问题")
    
    # 评审内容
    summary = fields.TextField(null=True, description="评审摘要")
    recommendations = fields.TextField(null=True, description="改进建议")
    specialized_analyses = fields.JSONField(default=dict, description="专项分析详情")
    
    # 元数据
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "review_reports"
        table_description = "评审报告表"


class ReviewIssue(Model):
    """评审问题模型"""
    id = fields.CharField(max_length=36, pk=True)
    report_id = fields.CharField(max_length=36, description="所属报告ID")
    module_id = fields.CharField(max_length=36, null=True, description="相关模块ID")
    
    # 问题信息
    issue_type = fields.CharField(max_length=20, description="问题类型")
    priority = fields.CharField(max_length=10, description="优先级")
    title = fields.CharField(max_length=200, description="问题标题")
    description = fields.TextField(description="问题描述")
    suggestion = fields.TextField(null=True, description="改进建议")
    
    # 位置信息
    location = fields.CharField(max_length=200, null=True, description="问题位置")
    page_number = fields.IntField(null=True, description="页码")
    section = fields.CharField(max_length=100, null=True, description="章节")
    
    # 状态管理
    is_resolved = fields.BooleanField(default=False, description="已解决")
    resolution_note = fields.TextField(null=True, description="解决说明")
    
    # 元数据
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "review_issues"
        table_description = "评审问题表"


class ModuleReviewResult(Model):
    """模块评审结果模型"""
    id = fields.CharField(max_length=36, pk=True)
    report_id = fields.CharField(max_length=36, description="所属报告ID")
    module_id = fields.CharField(max_length=36, description="评审模块ID")
    
    # 模块基本信息
    module_id_str = fields.CharField(max_length=100, null=True, description="模块ID字符串")
    module_name = fields.CharField(max_length=200, null=True, description="模块名称")
    
    # 评审分数
    specification_score = fields.IntField(default=0, description="规格说明评分")
    clarity_score = fields.IntField(default=0, description="清晰度评分")
    completeness_score = fields.IntField(default=0, description="完整性评分")
    consistency_score = fields.IntField(default=0, description="一致性评分")
    feasibility_score = fields.IntField(default=0, description="可行性评分")
    overall_score = fields.IntField(default=0, description="总体评分")
    
    # 评审结果
    module_rating = fields.CharField(max_length=20, null=True, description="模块评价")
    issues_count = fields.IntField(default=0, description="问题数量")
    severity_score = fields.IntField(default=0, description="严重程度评分")
    
    # 详细分析 (JSON字段存储列表)
    issues = fields.JSONField(default=list, description="问题列表")
    strengths = fields.JSONField(default=list, description="优点列表")
    weaknesses = fields.JSONField(default=list, description="不足列表")
    recommendations = fields.JSONField(default=list, description="改进建议列表")
    
    # 文本分析内容
    analysis_content = fields.TextField(null=True, description="分析内容")
    
    # 元数据
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "module_review_results"
        table_description = "模块评审结果表"