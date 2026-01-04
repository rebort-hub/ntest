"""
智能编排系统相关的Schema
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class OrchestratorTaskBase(BaseModel):
    """智能编排任务基础Schema"""
    requirement: str = Field(..., description="需求描述")
    user_notes: Optional[str] = Field(None, description="用户备注")


class OrchestratorTaskCreate(OrchestratorTaskBase):
    """创建智能编排任务Schema"""
    project_id: int = Field(..., description="项目ID")
    chat_session_id: Optional[int] = Field(None, description="关联对话会话ID")


class OrchestratorTaskUpdate(BaseModel):
    """更新智能编排任务Schema"""
    status: Optional[str] = Field(None, description="状态")
    execution_plan: Optional[Dict[str, Any]] = Field(None, description="执行计划")
    execution_history: Optional[List[Dict[str, Any]]] = Field(None, description="执行历史")
    current_step: Optional[int] = Field(None, description="当前步骤")
    waiting_for: Optional[str] = Field(None, description="等待对象")
    user_notes: Optional[str] = Field(None, description="用户备注")
    requirement_analysis: Optional[Dict[str, Any]] = Field(None, description="需求分析结果")
    knowledge_docs: Optional[List[Dict[str, Any]]] = Field(None, description="检索的知识文档")
    testcases: Optional[List[Dict[str, Any]]] = Field(None, description="生成的测试用例")
    error_message: Optional[str] = Field(None, description="错误信息")


class OrchestratorTaskResponse(OrchestratorTaskBase):
    """智能编排任务响应Schema"""
    id: int
    user_id: int
    project_id: int
    chat_session_id: Optional[int]
    status: str
    execution_plan: Optional[Dict[str, Any]]
    execution_history: List[Dict[str, Any]]
    current_step: int
    waiting_for: Optional[str]
    requirement_analysis: Optional[Dict[str, Any]]
    knowledge_docs: List[Dict[str, Any]]
    testcases: List[Dict[str, Any]]
    execution_log: List[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class AgentTaskBase(BaseModel):
    """Agent任务基础Schema"""
    goal: str = Field(..., description="任务目标（用户原始请求）")
    max_steps: int = Field(default=500, description="最大步骤数")


class AgentTaskCreate(AgentTaskBase):
    """创建Agent任务Schema"""
    session_id: int = Field(..., description="关联会话ID")


class AgentTaskUpdate(BaseModel):
    """更新Agent任务Schema"""
    status: Optional[str] = Field(None, description="状态")
    current_step: Optional[int] = Field(None, description="当前步骤")
    final_response: Optional[str] = Field(None, description="最终响应")
    error_message: Optional[str] = Field(None, description="错误信息")


class AgentTaskResponse(AgentTaskBase):
    """Agent任务响应Schema"""
    id: int
    session_id: int
    status: str
    current_step: int
    final_response: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class AgentStepBase(BaseModel):
    """Agent步骤基础Schema"""
    step_number: int = Field(..., description="步骤序号")
    input_context: Dict[str, Any] = Field(default={}, description="输入上下文（精简版）")
    ai_thinking: Optional[str] = Field(None, description="AI思考过程")
    ai_decision: Optional[str] = Field(None, description="AI决策")
    tool_name: Optional[str] = Field(None, description="工具名称")
    tool_input: Optional[Dict[str, Any]] = Field(None, description="工具输入")
    tool_output_summary: Optional[str] = Field(None, description="工具输出摘要")
    tool_output_full_ref: Optional[str] = Field(None, description="完整输出引用")
    ai_response: Optional[str] = Field(None, description="AI响应")
    is_final: bool = Field(default=False, description="是否为最终响应")
    token_input: int = Field(default=0, description="输入Token数")
    token_output: int = Field(default=0, description="输出Token数")
    duration_ms: int = Field(default=0, description="耗时(毫秒)")


class AgentStepCreate(AgentStepBase):
    """创建Agent步骤Schema"""
    task_id: int = Field(..., description="所属任务ID")


class AgentStepUpdate(BaseModel):
    """更新Agent步骤Schema"""
    ai_thinking: Optional[str] = Field(None, description="AI思考过程")
    ai_decision: Optional[str] = Field(None, description="AI决策")
    tool_name: Optional[str] = Field(None, description="工具名称")
    tool_input: Optional[Dict[str, Any]] = Field(None, description="工具输入")
    tool_output_summary: Optional[str] = Field(None, description="工具输出摘要")
    tool_output_full_ref: Optional[str] = Field(None, description="完整输出引用")
    ai_response: Optional[str] = Field(None, description="AI响应")
    is_final: Optional[bool] = Field(None, description="是否为最终响应")
    token_input: Optional[int] = Field(None, description="输入Token数")
    token_output: Optional[int] = Field(None, description="输出Token数")
    duration_ms: Optional[int] = Field(None, description="耗时(毫秒)")


class AgentStepResponse(AgentStepBase):
    """Agent步骤响应Schema"""
    id: int
    task_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AgentBlackboardBase(BaseModel):
    """Agent黑板基础Schema"""
    history_summary: List[str] = Field(default=[], description="历史摘要列表")
    current_state: Dict[str, Any] = Field(default={}, description="当前状态")
    tool_results_refs: List[str] = Field(default=[], description="工具结果引用")
    context_variables: Dict[str, Any] = Field(default={}, description="上下文变量")


class AgentBlackboardCreate(AgentBlackboardBase):
    """创建Agent黑板Schema"""
    task_id: int = Field(..., description="所属任务ID")


class AgentBlackboardUpdate(BaseModel):
    """更新Agent黑板Schema"""
    history_summary: Optional[List[str]] = Field(None, description="历史摘要列表")
    current_state: Optional[Dict[str, Any]] = Field(None, description="当前状态")
    tool_results_refs: Optional[List[str]] = Field(None, description="工具结果引用")
    context_variables: Optional[Dict[str, Any]] = Field(None, description="上下文变量")


class AgentBlackboardResponse(AgentBlackboardBase):
    """Agent黑板响应Schema"""
    id: int
    task_id: int
    updated_at: datetime

    class Config:
        from_attributes = True


# 执行相关Schema
class TaskExecutionRequest(BaseModel):
    """任务执行请求Schema"""
    task_id: int = Field(..., description="任务ID")
    confirm_plan: bool = Field(default=False, description="确认执行计划")
    user_feedback: Optional[str] = Field(None, description="用户反馈")


class TaskExecutionResponse(BaseModel):
    """任务执行响应Schema"""
    task_id: int
    status: str
    current_step: int
    progress: float = Field(..., description="进度百分比")
    message: str = Field(..., description="状态消息")
    waiting_for_user: bool = Field(default=False, description="是否等待用户确认")


class StepExecutionRequest(BaseModel):
    """步骤执行请求Schema"""
    task_id: int = Field(..., description="任务ID")
    step_data: Dict[str, Any] = Field(..., description="步骤数据")


class StepExecutionResponse(BaseModel):
    """步骤执行响应Schema"""
    step_id: int
    task_id: int
    status: str
    result: Dict[str, Any] = Field(..., description="执行结果")
    is_final: bool = Field(..., description="是否为最终步骤")


# 黑板操作Schema
class BlackboardUpdateRequest(BaseModel):
    """黑板更新请求Schema"""
    task_id: int = Field(..., description="任务ID")
    operation: str = Field(..., description="操作类型")
    data: Dict[str, Any] = Field(..., description="更新数据")


class BlackboardQueryRequest(BaseModel):
    """黑板查询请求Schema"""
    task_id: int = Field(..., description="任务ID")
    query_type: str = Field(..., description="查询类型")
    filters: Optional[Dict[str, Any]] = Field(None, description="查询过滤器")


class BlackboardQueryResponse(BaseModel):
    """黑板查询响应Schema"""
    task_id: int
    data: Dict[str, Any] = Field(..., description="查询结果")
    timestamp: datetime = Field(..., description="查询时间")


# 批量操作Schema
class BatchTaskUpdateRequest(BaseModel):
    """批量任务更新请求Schema"""
    task_ids: List[int] = Field(..., description="任务ID列表")
    updates: Dict[str, Any] = Field(..., description="更新数据")


class TaskProgressResponse(BaseModel):
    """任务进度响应Schema"""
    task_id: int
    status: str
    progress: float
    current_step: int
    total_steps: int
    estimated_time: Optional[int] = Field(None, description="预计剩余时间(秒)")
    last_activity: datetime = Field(..., description="最后活动时间")