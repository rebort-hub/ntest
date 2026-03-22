# -*- coding: utf-8 -*-
"""
AI 代码生成相关的数据模式
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class ParameterLocation(str, Enum):
    """参数位置枚举"""
    QUERY = "query"
    PATH = "path"
    HEADER = "header"
    BODY = "body"


class ParameterType(str, Enum):
    """参数类型枚举"""
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


class APIParameter(BaseModel):
    """API参数模型"""
    name: str = Field(..., description="参数名称")
    type: ParameterType = Field(default=ParameterType.STRING, description="参数类型")
    in_: ParameterLocation = Field(default=ParameterLocation.QUERY, description="参数位置", alias="in")
    description: Optional[str] = Field(None, description="参数描述")
    required: bool = Field(default=False, description="是否必填")
    example: Optional[str] = Field(None, description="示例值")


class AICodeGenerateRequest(BaseModel):
    """AI代码生成请求"""
    path: str = Field(..., description="接口路径")
    method: str = Field(..., description="请求方法")
    summary: Optional[str] = Field(None, description="接口描述")
    parameters: List[APIParameter] = Field(default=[], description="接口参数")
    request_body: Optional[str] = Field(None, description="请求体JSON")
    response_example: Optional[str] = Field(None, description="响应示例JSON")
    framework: Optional[str] = Field(default="pytest", description="测试框架")
    tags: Optional[List[str]] = Field(default=[], description="接口标签")


class AICodeGenerateResponse(BaseModel):
    """AI代码生成响应"""
    code: str = Field(..., description="生成的测试代码")
    fileName: str = Field(..., description="建议的文件名")
    language: str = Field(default="python", description="代码语言")
    framework: str = Field(default="pytest", description="测试框架")
    generatedAt: str = Field(..., description="生成时间")
    codeLines: Optional[int] = Field(None, description="代码行数")


class SwaggerImportRequest(BaseModel):
    """Swagger导入请求"""
    swagger_url: str = Field(..., description="Swagger文档URL")
    selected_endpoints: Optional[List[str]] = Field(default=[], description="选择的接口ID列表")
    auto_generate: bool = Field(default=False, description="是否自动生成代码")


class SwaggerEndpoint(BaseModel):
    """Swagger接口信息"""
    id: str = Field(..., description="接口唯一标识")
    path: str = Field(..., description="接口路径")
    method: str = Field(..., description="请求方法")
    summary: Optional[str] = Field(None, description="接口摘要")
    description: Optional[str] = Field(None, description="接口描述")
    parameters: List[APIParameter] = Field(default=[], description="接口参数")
    request_body: Optional[dict] = Field(None, description="请求体结构")
    responses: Optional[dict] = Field(None, description="响应结构")
    tags: Optional[List[str]] = Field(default=[], description="接口标签")


class SwaggerImportResponse(BaseModel):
    """Swagger导入响应"""
    endpoints: List[SwaggerEndpoint] = Field(..., description="解析的接口列表")
    total_count: int = Field(..., description="接口总数")
    imported_count: int = Field(default=0, description="已导入数量")
    generated_count: int = Field(default=0, description="已生成代码数量")


class GenerationStats(BaseModel):
    """生成统计信息"""
    today_generated: int = Field(default=0, description="今日生成数量")
    total_generated: int = Field(default=0, description="总生成数量")
    success_rate: float = Field(default=100.0, description="成功率")
    avg_response_time: float = Field(default=0.0, description="平均响应时间(秒)")
    popular_endpoints: Optional[List[dict]] = Field(default=[], description="热门接口")


class CodeTemplate(BaseModel):
    """代码模板"""
    id: str = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    language: str = Field(..., description="编程语言")
    framework: str = Field(..., description="测试框架")
    template_content: str = Field(..., description="模板内容")
    variables: Optional[List[str]] = Field(default=[], description="模板变量")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")


class GenerationHistoryItem(BaseModel):
    """生成历史记录项"""
    id: int = Field(..., description="记录ID")
    path: str = Field(..., description="接口路径")
    method: str = Field(..., description="请求方法")
    summary: Optional[str] = Field(None, description="接口描述")
    file_name: str = Field(..., description="文件名")
    generated_code: str = Field(..., description="生成的代码")
    language: str = Field(..., description="编程语言")
    framework: str = Field(..., description="测试框架")
    code_lines: Optional[int] = Field(None, description="代码行数")
    generation_time: Optional[float] = Field(None, description="生成耗时")
    download_count: int = Field(default=0, description="下载次数")
    copy_count: int = Field(default=0, description="复制次数")
    create_time: str = Field(..., description="创建时间")
    last_used_time: Optional[str] = Field(None, description="最后使用时间")


class GenerationHistoryListRequest(BaseModel):
    """生成历史列表请求"""
    page_no: int = Field(default=1, description="页码")
    page_size: int = Field(default=20, description="每页大小")
    method: Optional[str] = Field(None, description="请求方法筛选")
    path: Optional[str] = Field(None, description="路径关键词筛选")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")


class GenerationHistoryListResponse(BaseModel):
    """生成历史列表响应"""
    data: List[GenerationHistoryItem] = Field(..., description="历史记录列表")
    total: int = Field(..., description="总记录数")
    page_no: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")


class UpdateUsageStatsRequest(BaseModel):
    """更新使用统计请求"""
    record_id: int = Field(..., description="记录ID")
    action: str = Field(..., description="操作类型: copy/download")


class DeleteHistoryRequest(BaseModel):
    """删除历史记录请求"""
    record_ids: List[int] = Field(..., description="要删除的记录ID列表")