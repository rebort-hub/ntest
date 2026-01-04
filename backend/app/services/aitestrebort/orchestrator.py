"""
智能编排服务
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.aitestrebort.orchestrator import (
    OrchestratorTask, AgentTask, AgentStep, AgentBlackboard
)
from app.schemas.aitestrebort.orchestrator import (
    OrchestratorTaskCreate, OrchestratorTaskUpdate,
    AgentTaskCreate, AgentTaskUpdate,
    AgentStepCreate, AgentStepUpdate,
    AgentBlackboardCreate, AgentBlackboardUpdate,
    TaskExecutionRequest, TaskExecutionResponse,
    StepExecutionRequest, StepExecutionResponse,
    BlackboardUpdateRequest, BlackboardQueryRequest, BlackboardQueryResponse,
    BatchTaskUpdateRequest, TaskProgressResponse
)

logger = logging.getLogger(__name__)


class OrchestratorService:
    """智能编排服务类"""
    
    # ==================== 智能编排任务管理 ====================
    
    @staticmethod
    async def create_orchestrator_task(
        task_data: OrchestratorTaskCreate,
        user_id: int
    ) -> OrchestratorTask:
        """创建智能编排任务"""
        try:
            return await OrchestratorTask.create(
                user_id=user_id,
                project_id=task_data.project_id,
                chat_session_id=task_data.chat_session_id,
                requirement=task_data.requirement,
                user_notes=task_data.user_notes,
                status="pending"
            )
        except Exception as e:
            logger.error(f"Create orchestrator task failed: {e}")
            raise
    
    @staticmethod
    async def list_orchestrator_tasks(
        user_id: int,
        project_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[OrchestratorTask]:
        """获取智能编排任务列表"""
        try:
            query = OrchestratorTask.filter(user_id=user_id)
            
            if project_id:
                query = query.filter(project_id=project_id)
            if status:
                query = query.filter(status=status)
            
            return await query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"List orchestrator tasks failed: {e}")
            raise
    
    @staticmethod
    async def update_orchestrator_task(
        task_id: int,
        task_update: OrchestratorTaskUpdate,
        user_id: int
    ) -> OrchestratorTask:
        """更新智能编排任务"""
        try:
            await OrchestratorTask.filter(id=task_id, user_id=user_id).update(
                **task_update.model_dump(exclude_unset=True)
            )
            return await OrchestratorTask.get(id=task_id)
        except Exception as e:
            logger.error(f"Update orchestrator task failed: {e}")
            raise
    
    @staticmethod
    async def delete_orchestrator_task(task_id: int, user_id: int):
        """删除智能编排任务"""
        try:
            await OrchestratorTask.filter(id=task_id, user_id=user_id).delete()
        except Exception as e:
            logger.error(f"Delete orchestrator task failed: {e}")
            raise
    
    @staticmethod
    async def execute_orchestrator_task(
        task_id: int,
        execution_request: TaskExecutionRequest,
        user_id: int
    ) -> TaskExecutionResponse:
        """执行智能编排任务"""
        try:
            task = await OrchestratorTask.get_or_none(id=task_id, user_id=user_id)
            if not task:
                raise ValueError("Task not found")
            
            # 更新任务状态
            await OrchestratorTask.filter(id=task_id).update(
                status="executing",
                started_at=datetime.now()
            )
            
            # 异步执行任务
            asyncio.create_task(
                OrchestratorService._execute_task_async(task_id, execution_request)
            )
            
            return TaskExecutionResponse(
                task_id=task_id,
                status="executing",
                current_step=0,
                progress=0.0,
                message="Task execution started",
                waiting_for_user=False
            )
            
        except Exception as e:
            logger.error(f"Execute orchestrator task failed: {e}")
            raise
    
    @staticmethod
    async def _execute_task_async(
        task_id: int,
        execution_request: TaskExecutionRequest
    ):
        """异步执行任务"""
        try:
            task = await OrchestratorTask.get(id=task_id)
            
            # 使用AI服务进行需求分析
            from app.services.ai.llm_service import get_llm_service
            
            llm_service = await get_llm_service()
            
            # 步骤1: 需求分析
            await OrchestratorTask.filter(id=task_id).update(
                current_step=1,
                execution_history=task.execution_history + [
                    {
                        "step": 1,
                        "name": "需求分析",
                        "status": "running",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            )
            
            # 使用AI分析需求
            requirement_analysis = await llm_service.analyze_requirement(task.requirement)
            
            await OrchestratorTask.filter(id=task_id).update(
                requirement_analysis=requirement_analysis,
                execution_history=task.execution_history + [
                    {
                        "step": 1,
                        "name": "需求分析",
                        "status": "completed",
                        "timestamp": datetime.now().isoformat(),
                        "result": "需求分析完成"
                    }
                ]
            )
            
            await asyncio.sleep(2)
            
            # 步骤2: 知识库检索
            await OrchestratorTask.filter(id=task_id).update(
                current_step=2,
                execution_history=task.execution_history + [
                    {
                        "step": 2,
                        "name": "知识库检索",
                        "status": "running",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            )
            
            # 模拟知识库检索
            knowledge_docs = [
                {
                    "title": "相关技术文档",
                    "type": "技术规范",
                    "relevance": 0.85,
                    "content": "相关的技术实现说明"
                }
            ]
            
            await OrchestratorTask.filter(id=task_id).update(
                knowledge_docs=knowledge_docs,
                execution_history=task.execution_history + [
                    {
                        "step": 2,
                        "name": "知识库检索",
                        "status": "completed",
                        "timestamp": datetime.now().isoformat(),
                        "result": f"检索到{len(knowledge_docs)}个相关文档"
                    }
                ]
            )
            
            await asyncio.sleep(2)
            
            # 步骤3: 生成执行计划
            await OrchestratorTask.filter(id=task_id).update(
                current_step=3,
                execution_history=task.execution_history + [
                    {
                        "step": 3,
                        "name": "生成执行计划",
                        "status": "running",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            )
            
            execution_plan = {
                "steps": [
                    {"name": "需求分析", "status": "completed"},
                    {"name": "知识库检索", "status": "completed"},
                    {"name": "生成执行计划", "status": "running"},
                    {"name": "执行任务", "status": "pending"},
                    {"name": "生成结果", "status": "pending"}
                ],
                "estimated_time": "10-15分钟"
            }
            
            await OrchestratorTask.filter(id=task_id).update(
                execution_plan=execution_plan,
                execution_history=task.execution_history + [
                    {
                        "step": 3,
                        "name": "生成执行计划",
                        "status": "completed",
                        "timestamp": datetime.now().isoformat(),
                        "result": "执行计划生成完成"
                    }
                ]
            )
            
            await asyncio.sleep(2)
            
            # 步骤4: 执行任务（生成测试用例）
            await OrchestratorTask.filter(id=task_id).update(
                current_step=4,
                execution_history=task.execution_history + [
                    {
                        "step": 4,
                        "name": "执行任务",
                        "status": "running",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            )
            
            # 使用AI生成测试用例
            test_cases = await llm_service.generate_test_cases(task.requirement)
            
            await OrchestratorTask.filter(id=task_id).update(
                testcases=test_cases,
                execution_history=task.execution_history + [
                    {
                        "step": 4,
                        "name": "执行任务",
                        "status": "completed",
                        "timestamp": datetime.now().isoformat(),
                        "result": f"生成了{len(test_cases)}个测试用例"
                    }
                ]
            )
            
            await asyncio.sleep(2)
            
            # 步骤5: 生成结果
            await OrchestratorTask.filter(id=task_id).update(
                current_step=5,
                execution_history=task.execution_history + [
                    {
                        "step": 5,
                        "name": "生成结果",
                        "status": "running",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            )
            
            await asyncio.sleep(1)
            
            # 完成任务
            await OrchestratorTask.filter(id=task_id).update(
                status="completed",
                completed_at=datetime.now(),
                execution_history=task.execution_history + [
                    {
                        "step": 5,
                        "name": "生成结果",
                        "status": "completed",
                        "timestamp": datetime.now().isoformat(),
                        "result": "任务执行完成"
                    }
                ]
            )
            
        except Exception as e:
            logger.error(f"Execute task async failed: {e}")
            await OrchestratorTask.filter(id=task_id).update(
                status="failed",
                error_message=str(e)
            )
    
    @staticmethod
    async def get_orchestrator_task_progress(
        task_id: int,
        user_id: int
    ) -> TaskProgressResponse:
        """获取智能编排任务进度"""
        try:
            task = await OrchestratorTask.get_or_none(id=task_id, user_id=user_id)
            if not task:
                raise ValueError("Task not found")
            
            # 计算进度
            progress_map = {
                "pending": 0.0,
                "planning": 20.0,
                "waiting_confirmation": 40.0,
                "executing": 60.0,
                "completed": 100.0,
                "failed": 0.0,
                "cancelled": 0.0
            }
            
            progress = progress_map.get(task.status, 0.0)
            total_steps = 5  # 总步骤数
            
            # 估算剩余时间
            estimated_time = None
            if task.status == "executing":
                remaining_steps = total_steps - task.current_step
                estimated_time = remaining_steps * 30  # 每步30秒
            
            return TaskProgressResponse(
                task_id=task_id,
                status=task.status,
                progress=progress,
                current_step=task.current_step,
                total_steps=total_steps,
                estimated_time=estimated_time,
                last_activity=task.updated_at or task.created_at
            )
            
        except Exception as e:
            logger.error(f"Get orchestrator task progress failed: {e}")
            raise
    
    @staticmethod
    async def cancel_orchestrator_task(task_id: int, user_id: int):
        """取消智能编排任务"""
        try:
            await OrchestratorTask.filter(id=task_id, user_id=user_id).update(
                status="cancelled",
                completed_at=datetime.now()
            )
        except Exception as e:
            logger.error(f"Cancel orchestrator task failed: {e}")
            raise
    
    # ==================== Agent任务管理 ====================
    
    @staticmethod
    async def create_agent_task(task_data: AgentTaskCreate) -> AgentTask:
        """创建Agent任务"""
        try:
            return await AgentTask.create(
                session_id=task_data.session_id,
                goal=task_data.goal,
                max_steps=task_data.max_steps,
                status="pending"
            )
        except Exception as e:
            logger.error(f"Create agent task failed: {e}")
            raise
    
    @staticmethod
    async def list_agent_tasks(
        session_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AgentTask]:
        """获取Agent任务列表"""
        try:
            query = AgentTask.all()
            
            if session_id:
                query = query.filter(session_id=session_id)
            if status:
                query = query.filter(status=status)
            
            return await query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"List agent tasks failed: {e}")
            raise
    
    @staticmethod
    async def update_agent_task(
        task_id: int,
        task_update: AgentTaskUpdate
    ) -> AgentTask:
        """更新Agent任务"""
        try:
            await AgentTask.filter(id=task_id).update(
                **task_update.model_dump(exclude_unset=True)
            )
            return await AgentTask.get(id=task_id)
        except Exception as e:
            logger.error(f"Update agent task failed: {e}")
            raise
    
    @staticmethod
    async def delete_agent_task(task_id: int):
        """删除Agent任务"""
        try:
            await AgentTask.filter(id=task_id).delete()
        except Exception as e:
            logger.error(f"Delete agent task failed: {e}")
            raise
    
    @staticmethod
    async def execute_agent_step(
        task_id: int,
        step_request: StepExecutionRequest
    ) -> StepExecutionResponse:
        """执行Agent步骤"""
        try:
            task = await AgentTask.get_or_none(id=task_id)
            if not task:
                raise ValueError("Task not found")
            
            # 创建步骤记录
            step = await AgentStep.create(
                task_id=task_id,
                step_number=task.current_step + 1,
                input_context=step_request.step_data,
                ai_thinking="正在分析输入...",
                ai_decision="决定执行工具调用",
                tool_name="example_tool",
                tool_input=step_request.step_data,
                tool_output_summary="工具执行成功",
                ai_response="步骤执行完成",
                is_final=False
            )
            
            # 更新任务状态
            await AgentTask.filter(id=task_id).update(
                current_step=task.current_step + 1,
                status="running"
            )
            
            return StepExecutionResponse(
                step_id=step.id,
                task_id=task_id,
                status="completed",
                result={"message": "Step executed successfully"},
                is_final=False
            )
            
        except Exception as e:
            logger.error(f"Execute agent step failed: {e}")
            raise
    
    @staticmethod
    async def get_agent_task_progress(task_id: int) -> TaskProgressResponse:
        """获取Agent任务进度"""
        try:
            task = await AgentTask.get_or_none(id=task_id)
            if not task:
                raise ValueError("Task not found")
            
            progress = (task.current_step / task.max_steps) * 100
            
            return TaskProgressResponse(
                task_id=task_id,
                status=task.status,
                progress=progress,
                current_step=task.current_step,
                total_steps=task.max_steps,
                estimated_time=None,
                last_activity=task.updated_at
            )
            
        except Exception as e:
            logger.error(f"Get agent task progress failed: {e}")
            raise
    
    # ==================== Agent步骤管理 ====================
    
    @staticmethod
    async def create_agent_step(step_data: AgentStepCreate) -> AgentStep:
        """创建Agent步骤"""
        try:
            return await AgentStep.create(**step_data.model_dump())
        except Exception as e:
            logger.error(f"Create agent step failed: {e}")
            raise
    
    @staticmethod
    async def list_agent_steps(
        task_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AgentStep]:
        """获取Agent步骤列表"""
        try:
            query = AgentStep.all()
            
            if task_id:
                query = query.filter(task_id=task_id)
            
            return await query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"List agent steps failed: {e}")
            raise
    
    @staticmethod
    async def update_agent_step(
        step_id: int,
        step_update: AgentStepUpdate
    ) -> AgentStep:
        """更新Agent步骤"""
        try:
            await AgentStep.filter(id=step_id).update(
                **step_update.model_dump(exclude_unset=True)
            )
            return await AgentStep.get(id=step_id)
        except Exception as e:
            logger.error(f"Update agent step failed: {e}")
            raise
    
    @staticmethod
    async def delete_agent_step(step_id: int):
        """删除Agent步骤"""
        try:
            await AgentStep.filter(id=step_id).delete()
        except Exception as e:
            logger.error(f"Delete agent step failed: {e}")
            raise
    
    # ==================== Agent黑板管理 ====================
    
    @staticmethod
    async def create_agent_blackboard(
        blackboard_data: AgentBlackboardCreate
    ) -> AgentBlackboard:
        """创建Agent黑板"""
        try:
            return await AgentBlackboard.create(**blackboard_data.model_dump())
        except Exception as e:
            logger.error(f"Create agent blackboard failed: {e}")
            raise
    
    @staticmethod
    async def update_agent_blackboard(
        task_id: int,
        blackboard_update: AgentBlackboardUpdate
    ) -> AgentBlackboard:
        """更新Agent黑板"""
        try:
            await AgentBlackboard.filter(task_id=task_id).update(
                **blackboard_update.model_dump(exclude_unset=True)
            )
            return await AgentBlackboard.get(task_id=task_id)
        except Exception as e:
            logger.error(f"Update agent blackboard failed: {e}")
            raise
    
    @staticmethod
    async def update_blackboard_data(
        task_id: int,
        update_request: BlackboardUpdateRequest
    ):
        """更新黑板数据"""
        try:
            blackboard = await AgentBlackboard.get_or_none(task_id=task_id)
            if not blackboard:
                # 创建黑板
                blackboard = await AgentBlackboard.create(task_id=task_id)
            
            if update_request.operation == "add_history":
                history = list(blackboard.history_summary)
                history.append(str(update_request.data.get("summary", "")))
                await AgentBlackboard.filter(task_id=task_id).update(
                    history_summary=history
                )
            elif update_request.operation == "update_state":
                state = dict(blackboard.current_state)
                state.update(update_request.data)
                await AgentBlackboard.filter(task_id=task_id).update(
                    current_state=state
                )
            elif update_request.operation == "add_tool_result":
                refs = list(blackboard.tool_results_refs)
                refs.append(str(update_request.data.get("ref", "")))
                await AgentBlackboard.filter(task_id=task_id).update(
                    tool_results_refs=refs
                )
            
        except Exception as e:
            logger.error(f"Update blackboard data failed: {e}")
            raise
    
    @staticmethod
    async def query_blackboard_data(
        task_id: int,
        query_request: BlackboardQueryRequest
    ) -> BlackboardQueryResponse:
        """查询黑板数据"""
        try:
            blackboard = await AgentBlackboard.get_or_none(task_id=task_id)
            if not blackboard:
                raise ValueError("Blackboard not found")
            
            data = {}
            if query_request.query_type == "history":
                data = {"history": blackboard.history_summary}
            elif query_request.query_type == "state":
                data = {"state": blackboard.current_state}
            elif query_request.query_type == "tool_results":
                data = {"tool_results": blackboard.tool_results_refs}
            elif query_request.query_type == "all":
                data = {
                    "history": blackboard.history_summary,
                    "state": blackboard.current_state,
                    "tool_results": blackboard.tool_results_refs,
                    "context_variables": blackboard.context_variables
                }
            
            return BlackboardQueryResponse(
                task_id=task_id,
                data=data,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Query blackboard data failed: {e}")
            raise
    
    @staticmethod
    async def add_blackboard_history(task_id: int, summary: str):
        """添加黑板历史记录"""
        try:
            blackboard = await AgentBlackboard.get_or_none(task_id=task_id)
            if not blackboard:
                blackboard = await AgentBlackboard.create(task_id=task_id)
            
            history = list(blackboard.history_summary)
            history.append(summary)
            
            # 限制历史长度
            max_history = 100
            if len(history) > max_history:
                history = history[-max_history:]
            
            await AgentBlackboard.filter(task_id=task_id).update(
                history_summary=history
            )
            
        except Exception as e:
            logger.error(f"Add blackboard history failed: {e}")
            raise
    
    @staticmethod
    async def update_blackboard_state(task_id: int, key: str, value: dict):
        """更新黑板状态"""
        try:
            blackboard = await AgentBlackboard.get_or_none(task_id=task_id)
            if not blackboard:
                blackboard = await AgentBlackboard.create(task_id=task_id)
            
            state = dict(blackboard.current_state)
            state[key] = value
            
            await AgentBlackboard.filter(task_id=task_id).update(
                current_state=state
            )
            
        except Exception as e:
            logger.error(f"Update blackboard state failed: {e}")
            raise
    
    @staticmethod
    async def get_recent_blackboard_history(
        task_id: int,
        count: int = 10
    ) -> List[str]:
        """获取最近的黑板历史"""
        try:
            blackboard = await AgentBlackboard.get_or_none(task_id=task_id)
            if not blackboard:
                return []
            
            history = blackboard.history_summary or []
            return history[-count:] if len(history) > count else history
            
        except Exception as e:
            logger.error(f"Get recent blackboard history failed: {e}")
            raise
    
    @staticmethod
    async def compress_blackboard_history(
        task_id: int,
        context_limit: int = 128000,
        model_name: str = "gpt-4o"
    ) -> bool:
        """压缩黑板历史"""
        try:
            blackboard = await AgentBlackboard.get_or_none(task_id=task_id)
            if not blackboard:
                return False
            
            history = blackboard.history_summary or []
            if len(history) <= 10:  # 历史记录不多，不需要压缩
                return False
            
            # TODO: 实现AI压缩逻辑
            # 这里应该调用LLM对历史进行智能压缩
            
            # 模拟压缩：保留最近10条，其余压缩为摘要
            recent_history = history[-10:]
            compressed_summary = f"[历史压缩] 前{len(history)-10}条记录已压缩"
            
            new_history = [compressed_summary] + recent_history
            
            await AgentBlackboard.filter(task_id=task_id).update(
                history_summary=new_history
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Compress blackboard history failed: {e}")
            return False
    
    # ==================== 批量操作 ====================
    
    @staticmethod
    async def batch_update_orchestrator_tasks(
        batch_request: BatchTaskUpdateRequest,
        user_id: int
    ) -> List[OrchestratorTask]:
        """批量更新智能编排任务"""
        try:
            await OrchestratorTask.filter(
                id__in=batch_request.task_ids,
                user_id=user_id
            ).update(**batch_request.updates)
            
            return await OrchestratorTask.filter(
                id__in=batch_request.task_ids,
                user_id=user_id
            ).all()
            
        except Exception as e:
            logger.error(f"Batch update orchestrator tasks failed: {e}")
            raise
    
    @staticmethod
    async def batch_cancel_orchestrator_tasks(
        task_ids: List[int],
        user_id: int
    ):
        """批量取消智能编排任务"""
        try:
            await OrchestratorTask.filter(
                id__in=task_ids,
                user_id=user_id
            ).update(
                status="cancelled",
                completed_at=datetime.now()
            )
        except Exception as e:
            logger.error(f"Batch cancel orchestrator tasks failed: {e}")
            raise
    
    # ==================== 统计和监控 ====================
    
    @staticmethod
    async def get_orchestrator_statistics(
        user_id: int,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取智能编排统计信息"""
        try:
            query = OrchestratorTask.filter(user_id=user_id)
            if project_id:
                query = query.filter(project_id=project_id)
            
            total_tasks = await query.count()
            completed_tasks = await query.filter(status="completed").count()
            failed_tasks = await query.filter(status="failed").count()
            running_tasks = await query.filter(status="executing").count()
            
            return {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "running_tasks": running_tasks,
                "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Get orchestrator statistics failed: {e}")
            raise
    
    @staticmethod
    async def get_agent_statistics(
        session_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取Agent任务统计信息"""
        try:
            query = AgentTask.all()
            if session_id:
                query = query.filter(session_id=session_id)
            
            total_tasks = await query.count()
            completed_tasks = await query.filter(status="completed").count()
            failed_tasks = await query.filter(status="failed").count()
            running_tasks = await query.filter(status="running").count()
            
            return {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "running_tasks": running_tasks,
                "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Get agent statistics failed: {e}")
            raise
    
    @staticmethod
    async def get_system_health() -> Dict[str, Any]:
        """获取系统健康状态"""
        try:
            # 检查各种系统状态
            total_orchestrator_tasks = await OrchestratorTask.all().count()
            total_agent_tasks = await AgentTask.all().count()
            total_agent_steps = await AgentStep.all().count()
            total_blackboards = await AgentBlackboard.all().count()
            
            # 检查运行中的任务
            running_orchestrator_tasks = await OrchestratorTask.filter(
                status="executing"
            ).count()
            running_agent_tasks = await AgentTask.filter(status="running").count()
            
            return {
                "status": "healthy",
                "total_orchestrator_tasks": total_orchestrator_tasks,
                "total_agent_tasks": total_agent_tasks,
                "total_agent_steps": total_agent_steps,
                "total_blackboards": total_blackboards,
                "running_orchestrator_tasks": running_orchestrator_tasks,
                "running_agent_tasks": running_agent_tasks,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Get system health failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }