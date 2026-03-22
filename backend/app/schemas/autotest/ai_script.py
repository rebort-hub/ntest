# -*- coding: utf-8 -*-
"""
AI 自动化脚本生成相关的数据模式
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ScriptTypeEnum(str, Enum):
    """脚本类型枚举"""
    PYTEST = "pytest"
    TESTNG = "testng"
    JAVA_JUNIT = "java_junit"


class ScriptLanguageEnum(str, Enum):
    """脚本语言枚举"""
    PYTHON = "python"
    JAVA = "java"


class AIGenerateScriptRequest(BaseModel):
    """AI生成脚本请求"""
    api_ids: List[int] = Field(..., description="接口ID列表")
    script_type: ScriptTypeEnum = Field(..., description="脚本类型")
    script_language: ScriptLanguageEnum = Field(..., description="脚本语言")
    test_framework: str = Field(..., description="测试框架")
    include_assertions: bool = Field(default=True, description="是否包含断言")
    include_data_driven: bool = Field(default=False, description="是否包含数据驱动")
    custom_template: Optional[str] = Field(None, description="自定义模板")
    llm_config_id: Optional[int] = Field(None, description="LLM配置ID")


class SwaggerImportRequest(BaseModel):
    """Swagger导入请求"""
    swagger_url: str = Field(..., description="Swagger文档地址")
    project_id: int = Field(..., description="项目ID")
    module_id: int = Field(..., description="模块ID")
    auto_generate_script: bool = Field(default=False, description="是否自动生成脚本")
    script_config: Optional[AIGenerateScriptRequest] = Field(None, description="脚本生成配置")


class GeneratedScript(BaseModel):
    """生成的脚本"""
    api_id: int = Field(..., description="接口ID")
    api_name: str = Field(..., description="接口名称")
    script_content: str = Field(..., description="脚本内容")
    script_type: ScriptTypeEnum = Field(..., description="脚本类型")
    script_language: ScriptLanguageEnum = Field(..., description="脚本语言")
    file_name: str = Field(..., description="建议的文件名")


class AIScriptGenerateResponse(BaseModel):
    """AI脚本生成响应"""
    success_count: int = Field(..., description="成功生成数量")
    failed_count: int = Field(..., description="失败数量")
    generated_scripts: List[GeneratedScript] = Field(..., description="生成的脚本列表")
    failed_apis: List[Dict[str, Any]] = Field(default=[], description="失败的接口")
    total_lines: int = Field(..., description="总代码行数")