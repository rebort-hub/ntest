"""
智能编排系统模型
基于使用Tortoise ORM
"""
from tortoise.models import Model
from tortoise import fields
from enum import Enum


class OrchestratorTaskStatus(str, Enum):
    """智能编排任务状态"""
    PENDING = "pending"
    PLANNING = "planning"
    WAITING_CONFIRMATION = "waiting_confirmation"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentTaskStatus(str, Enum):
    """Agent任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class OrchestratorTask(Model):
    """智能编排任务"""
    id = fields.IntField(pk=True)
    user_id = fields.IntField(description="用户ID")
    project_id = fields.IntField(description="项目ID")
    chat_session_id = fields.IntField(null=True, description="关联对话会话ID")
    
    # 输入
    requirement = fields.TextField(description="需求描述")
    
    # 状态
    status = fields.CharField(max_length=30, default=OrchestratorTaskStatus.PENDING, description="状态")
    
    # 交互式执行相关
    execution_plan = fields.JSONField(null=True, description="执行计划")
    execution_history = fields.JSONField(default=list, description="执行历史")
    current_step = fields.IntField(default=0, description="当前步骤")
    waiting_for = fields.CharField(max_length=50, null=True, description="等待对象")
    user_notes = fields.TextField(null=True, description="用户备注")
    
    # 输出
    requirement_analysis = fields.JSONField(null=True, description="需求分析结果")
    knowledge_docs = fields.JSONField(default=list, description="检索的知识文档")
    testcases = fields.JSONField(default=list, description="生成的测试用例")
    
    # 执行记录(保留兼容性)
    execution_log = fields.JSONField(default=list, description="执行日志(旧)")
    error_message = fields.TextField(null=True, description="错误信息")
    
    # 时间
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    started_at = fields.DatetimeField(null=True, description="开始时间")
    completed_at = fields.DatetimeField(null=True, description="完成时间")

    class Meta:
        table = "orchestrator_tasks"
        table_description = "智能编排任务表"


class AgentTask(Model):
    """Agent Loop 任务 - 用于分步执行的任务管理"""
    id = fields.IntField(pk=True)
    session_id = fields.IntField(description="关联会话ID")
    goal = fields.TextField(description="任务目标（用户原始请求）")
    status = fields.CharField(max_length=20, default=AgentTaskStatus.PENDING, description="状态")
    max_steps = fields.IntField(default=500, description="最大步骤数")
    current_step = fields.IntField(default=0, description="当前步骤")
    final_response = fields.TextField(null=True, description="最终响应")
    error_message = fields.TextField(null=True, description="错误信息")
    
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    completed_at = fields.DatetimeField(null=True, description="完成时间")

    class Meta:
        table = "agent_tasks"
        table_description = "Agent任务表"


class AgentStep(Model):
    """Agent 单步执行记录"""
    id = fields.IntField(pk=True)
    task = fields.ForeignKeyField(
        'test_platform.AgentTask',
        related_name='steps',
        description="所属任务"
    )
    step_number = fields.IntField(description="步骤序号")
    
    # 输入
    input_context = fields.JSONField(default=dict, description="输入上下文（精简版）")
    
    # AI 决策
    ai_thinking = fields.TextField(null=True, description="AI思考过程")
    ai_decision = fields.TextField(null=True, description="AI决策")
    
    # 工具调用
    tool_name = fields.CharField(max_length=100, null=True, description="工具名称")
    tool_input = fields.JSONField(null=True, description="工具输入")
    tool_output_summary = fields.TextField(null=True, description="工具输出摘要")
    tool_output_full_ref = fields.CharField(max_length=200, null=True, description="完整输出引用")
    
    # AI 响应
    ai_response = fields.TextField(null=True, description="AI响应")
    is_final = fields.BooleanField(default=False, description="是否为最终响应")
    
    # 统计
    token_input = fields.IntField(default=0, description="输入Token数")
    token_output = fields.IntField(default=0, description="输出Token数")
    duration_ms = fields.IntField(default=0, description="耗时(毫秒)")
    
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "agent_steps"
        table_description = "Agent步骤表"
        unique_together = (("task", "step_number"),)


class AgentBlackboard(Model):
    """Agent 黑板 - 任务执行过程中的状态共享"""
    id = fields.IntField(pk=True)
    task = fields.OneToOneField(
        'test_platform.AgentTask',
        related_name='blackboard',
        description="所属任务"
    )
    
    # 历史摘要（精简版，供 AI 参考）
    history_summary = fields.JSONField(default=list, description="历史摘要列表")
    
    # 当前状态（如当前页面 URL、已完成的子任务等）
    current_state = fields.JSONField(default=dict, description="当前状态")
    
    # 工具结果引用列表（完整结果的存储位置）
    tool_results_refs = fields.JSONField(default=list, description="工具结果引用")
    
    # 上下文变量（可供工具使用的变量）
    context_variables = fields.JSONField(default=dict, description="上下文变量")
    
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "agent_blackboards"
        table_description = "Agent黑板表"