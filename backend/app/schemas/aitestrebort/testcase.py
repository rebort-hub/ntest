"""
aitestrebort 测试用例管理数据模式
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.base_form import PaginationForm


class aitestrebortTestCaseQueryForm(PaginationForm):
    """测试用例查询表单"""
    search: Optional[str] = Field(None, description="搜索关键词")
    module_id: Optional[int] = Field(None, description="模块ID")
    level: Optional[str] = Field(None, description="用例等级")
    
    def get_query_filter(self, *args, **kwargs):
        """查询条件"""
        filter_dict = {}
        if self.search:
            filter_dict["search"] = self.search
        if self.module_id:
            filter_dict["module_id"] = self.module_id
        if self.level:
            filter_dict["level"] = self.level
        return filter_dict


class aitestrebortTestCaseModuleQueryForm(PaginationForm):
    """测试用例模块查询表单"""
    search: Optional[str] = Field(None, description="搜索关键词")
    parent_id: Optional[int] = Field(None, description="父模块ID")
    
    def get_query_filter(self, *args, **kwargs):
        """查询条件"""
        filter_dict = {}
        if self.search:
            filter_dict["search"] = self.search
        if self.parent_id:
            filter_dict["parent_id"] = self.parent_id
        return filter_dict


class aitestrebortTestCaseStepSchema(BaseModel):
    """测试用例步骤模式"""
    id: Optional[int] = None
    step_number: int = Field(..., description="步骤编号")
    description: str = Field(..., description="步骤描述")
    expected_result: str = Field(..., description="预期结果")
    creator_id: Optional[int] = Field(None, description="创建人ID")
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class aitestrebortTestCaseScreenshotSchema(BaseModel):
    """测试用例截图模式"""
    id: Optional[int] = None
    screenshot_path: str = Field(..., description="截图路径")
    title: Optional[str] = Field(None, description="图片标题")
    description: Optional[str] = Field(None, description="图片描述")
    step_number: Optional[int] = Field(None, description="对应步骤")
    mcp_session_id: Optional[str] = Field(None, description="MCP会话ID")
    page_url: Optional[str] = Field(None, description="页面URL")
    uploader_id: Optional[int] = Field(None, description="上传人ID")
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class aitestrebortTestCaseModuleSchema(BaseModel):
    """测试用例模块模式"""
    id: Optional[int] = None
    name: str = Field(..., max_length=100, description="模块名称")
    parent_id: Optional[int] = Field(None, description="父模块ID")
    level: int = Field(1, description="模块级别")
    creator_id: Optional[int] = Field(None, description="创建人ID")
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    
    # 子模块
    children: Optional[List['aitestrebortTestCaseModuleSchema']] = []
    testcase_count: Optional[int] = 0

    class Config:
        from_attributes = True


class aitestrebortTestCaseSchema(BaseModel):
    """测试用例模式"""
    id: Optional[int] = None
    name: str = Field(..., max_length=255, description="用例名称")
    precondition: Optional[str] = Field(None, description="前置条件")
    level: str = Field("P2", description="用例等级")
    module_id: int = Field(..., description="所属模块ID")
    creator_id: Optional[int] = Field(None, description="创建人ID")
    notes: Optional[str] = Field(None, description="备注")
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    
    # 关联数据
    steps: Optional[List[aitestrebortTestCaseStepSchema]] = []
    screenshots: Optional[List[aitestrebortTestCaseScreenshotSchema]] = []
    
    # 扩展信息
    module_name: Optional[str] = None
    step_count: Optional[int] = 0

    class Config:
        from_attributes = True


class aitestrebortTestCaseCreateSchema(BaseModel):
    """创建测试用例模式"""
    name: str = Field(..., max_length=255, description="用例名称")
    description: Optional[str] = Field(None, description="用例描述")
    module_id: int = Field(..., description="所属模块ID")
    precondition: Optional[str] = Field(None, description="前置条件")
    level: str = Field("P2", description="用例等级")
    notes: Optional[str] = Field(None, description="备注")


class aitestrebortTestCaseUpdateSchema(BaseModel):
    """更新测试用例模式"""
    name: Optional[str] = Field(None, max_length=255, description="用例名称")
    description: Optional[str] = Field(None, description="用例描述")
    module_id: Optional[int] = Field(None, description="所属模块ID")
    precondition: Optional[str] = Field(None, description="前置条件")
    level: Optional[str] = Field(None, description="用例等级")
    notes: Optional[str] = Field(None, description="备注")


class aitestrebortTestCaseStepCreateSchema(BaseModel):
    """创建测试步骤模式"""
    step_number: int = Field(..., description="步骤编号")
    description: str = Field(..., description="步骤描述")
    expected_result: str = Field(..., description="预期结果")


class aitestrebortTestCaseModuleCreateSchema(BaseModel):
    """创建测试模块模式"""
    name: str = Field(..., max_length=100, description="模块名称")
    description: Optional[str] = Field(None, description="模块描述")
    parent_id: Optional[int] = Field(None, description="父模块ID")


class aitestrebortTestSuiteSchema(BaseModel):
    """测试套件模式"""
    id: Optional[int] = None
    name: str = Field(..., max_length=255, description="套件名称")
    description: Optional[str] = Field(None, description="套件描述")
    project_id: int = Field(..., description="所属项目ID")
    creator_id: Optional[int] = Field(None, description="创建人ID")
    parallel_count: int = Field(1, description="并行数量")
    timeout: int = Field(300, description="超时时间(秒)")
    status: str = Field("active", description="状态")
    last_execution: Optional[datetime] = Field(None, description="最后执行时间")
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    
    # 关联的测试用例
    testcases: Optional[List[aitestrebortTestCaseSchema]] = []
    testcase_count: Optional[int] = 0

    class Config:
        from_attributes = True


class aitestrebortTestSuiteCreateSchema(BaseModel):
    """创建测试套件模式"""
    name: str = Field(..., max_length=255, description="套件名称")
    description: Optional[str] = Field(None, description="套件描述")
    project_id: int = Field(..., description="所属项目ID")
    max_concurrent_tasks: Optional[int] = Field(1, description="最大并发数")
    timeout: Optional[int] = Field(300, description="超时时间(秒)")
    status: Optional[str] = Field("active", description="状态")
    testcase_ids: Optional[List[int]] = Field([], description="测试用例ID列表")


class aitestrebortTestSuiteUpdateSchema(BaseModel):
    """更新测试套件模式"""
    name: Optional[str] = Field(None, max_length=255, description="套件名称")
    description: Optional[str] = Field(None, description="套件描述")
    max_concurrent_tasks: Optional[int] = Field(None, description="最大并发数")
    timeout: Optional[int] = Field(None, description="超时时间(秒)")
    status: Optional[str] = Field(None, description="状态")
    testcase_ids: Optional[List[int]] = Field(None, description="测试用例ID列表")


class aitestrebortTestCaseStepUpdateSchema(BaseModel):
    """更新测试步骤模式"""
    step_number: Optional[int] = Field(None, description="步骤编号")
    description: Optional[str] = Field(None, description="步骤描述")
    expected_result: Optional[str] = Field(None, description="预期结果")


class aitestrebortTestCaseModuleUpdateSchema(BaseModel):
    """更新测试模块模式"""
    name: Optional[str] = Field(None, max_length=100, description="模块名称")
    parent_id: Optional[int] = Field(None, description="父模块ID")


class aitestrebortTestExecutionSchema(BaseModel):
    """测试执行记录模式"""
    id: Optional[int] = None
    suite_id: int = Field(..., description="测试套件ID")
    status: str = Field("pending", description="执行状态")
    executor_id: Optional[int] = Field(None, description="执行人ID")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # 统计信息
    total_count: int = 0
    passed_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    error_count: int = 0
    
    celery_task_id: Optional[str] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    
    # 扩展信息
    suite_name: Optional[str] = None
    pass_rate: Optional[float] = 0.0
    duration: Optional[float] = None

    class Config:
        from_attributes = True


class aitestrebortTestCaseResultSchema(BaseModel):
    """测试用例执行结果模式"""
    id: Optional[int] = None
    execution_id: int = Field(..., description="测试执行ID")
    testcase_id: int = Field(..., description="测试用例ID")
    status: str = Field("pending", description="执行状态")
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    mcp_session_id: Optional[str] = None
    screenshots: Optional[List[str]] = []
    execution_log: Optional[str] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    
    # 扩展信息
    testcase_name: Optional[str] = None
    duration: Optional[float] = None

    class Config:
        from_attributes = True


class aitestrebortTestCaseListSchema(BaseModel):
    """测试用例列表模式"""
    id: int
    name: str
    level: str
    module_id: int
    module_name: Optional[str] = None
    creator_id: Optional[int] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    step_count: int = 0

    class Config:
        from_attributes = True


class aitestrebortAIGenerateTestCaseSchema(BaseModel):
    """AI生成测试用例请求模式"""
    requirement: str = Field(..., description="需求描述")
    module_id: int = Field(..., description="所属模块ID")
    count: int = Field(1, description="生成数量", ge=1, le=10)
    context: Optional[str] = Field(None, description="上下文信息")
    llm_config_id: Optional[int] = Field(None, description="LLM配置ID")
    source_type: Optional[str] = Field("manual", description="需求来源类型：manual(手动输入)、document(需求文档)、requirement(需求条目)、module(需求模块)")
    source_id: Optional[str] = Field(None, description="来源ID（需求文档ID、需求ID、模块ID等）")
    prompt_id: Optional[int] = Field(None, description="系统提示词ID")
    enable_knowledge: Optional[bool] = Field(False, description="是否启用知识库")
    knowledge_base_ids: Optional[List[str]] = Field(None, description="关联的知识库ID列表")


class aitestrebortAIOptimizeTestCaseSchema(BaseModel):
    """AI优化测试用例请求模式"""
    optimization_request: str = Field(..., description="优化要求")
    llm_config_id: Optional[int] = Field(None, description="LLM配置ID")


class aitestrebortAIGenerateFromScreenshotSchema(BaseModel):
    """AI根据截图生成测试用例请求模式"""
    screenshot_description: str = Field(..., description="截图描述")
    module_id: int = Field(..., description="所属模块ID")
    page_url: Optional[str] = Field(None, description="页面URL")
    llm_config_id: Optional[int] = Field(None, description="LLM配置ID")


class aitestrebortAIBatchGenerateSchema(BaseModel):
    """AI批量生成测试用例请求模式"""
    requirements: List[str] = Field(..., description="需求描述列表")
    module_id: int = Field(..., description="所属模块ID")
    llm_config_id: Optional[int] = Field(None, description="LLM配置ID")


class aitestrebortAIGenerateScriptSchema(BaseModel):
    """AI生成自动化脚本请求模式"""
    script_type: str = Field("playwright", description="脚本类型")
    llm_config_id: Optional[int] = Field(None, description="LLM配置ID")


class aitestrebortRequirementSourceSchema(BaseModel):
    """需求来源模式 - 用于前端选择"""
    id: str
    name: str
    type: str  # document, requirement, module, manual
    description: Optional[str] = None
    content_preview: Optional[str] = None  # 内容预览
    
    class Config:
        from_attributes = True