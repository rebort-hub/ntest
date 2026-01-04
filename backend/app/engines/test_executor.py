"""
测试执行引擎
支持并发执行测试用例和脚本
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import json
import traceback
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from app.models.aitestrebort.testcase import (
    aitestrebortTestSuite, aitestrebortTestExecution, aitestrebortTestCaseResult,
    aitestrebortTestCase
)
from app.models.aitestrebort.automation import (
    aitestrebortAutomationScript, aitestrebortScriptExecution
)

logger = logging.getLogger(__name__)


class ExecutionStatus(str, Enum):
    """执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


@dataclass
class ExecutionResult:
    """执行结果"""
    status: ExecutionStatus
    message: str = ""
    error_message: str = ""
    stack_trace: str = ""
    execution_time: float = 0.0
    screenshots: List[str] = None
    logs: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.screenshots is None:
            self.screenshots = []
        if self.logs is None:
            self.logs = []
        if self.metadata is None:
            self.metadata = {}


class TestExecutor:
    """测试执行器"""
    
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.execution_callbacks: List[Callable] = []
    
    def add_execution_callback(self, callback: Callable):
        """添加执行回调"""
        self.execution_callbacks.append(callback)
    
    async def _notify_callbacks(self, event_type: str, data: Dict[str, Any]):
        """通知回调"""
        for callback in self.execution_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event_type, data)
                else:
                    callback(event_type, data)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    async def execute_test_suite(
        self,
        suite_id: int,
        executor_id: int,
        max_concurrent: Optional[int] = None
    ) -> int:
        """执行测试套件"""
        try:
            # 获取测试套件
            suite = await aitestrebortTestSuite.get_or_none(id=suite_id)
            if not suite:
                raise ValueError(f"Test suite not found: {suite_id}")
            
            # 创建执行记录
            execution = await aitestrebortTestExecution.create(
                suite_id=suite_id,
                executor_id=executor_id,
                status="running",
                started_at=datetime.now()
            )
            
            await self._notify_callbacks("execution_started", {
                "execution_id": execution.id,
                "suite_id": suite_id
            })
            
            # 获取测试用例
            test_cases = await self._get_suite_test_cases(suite_id)
            
            # 更新总数
            await aitestrebortTestExecution.filter(id=execution.id).update(
                total_count=len(test_cases)
            )
            
            # 并发执行测试用例
            max_concurrent = max_concurrent or suite.max_concurrent_tasks or self.max_concurrent
            
            results = await self._execute_test_cases_concurrent(
                execution.id, test_cases, max_concurrent
            )
            
            # 统计结果
            stats = self._calculate_execution_stats(results)
            
            # 更新执行记录
            await aitestrebortTestExecution.filter(id=execution.id).update(
                status="completed",
                completed_at=datetime.now(),
                passed_count=stats["passed"],
                failed_count=stats["failed"],
                error_count=stats["error"],
                skipped_count=stats["skipped"]
            )
            
            await self._notify_callbacks("execution_completed", {
                "execution_id": execution.id,
                "suite_id": suite_id,
                "stats": stats
            })
            
            return execution.id
            
        except Exception as e:
            logger.error(f"Test suite execution failed: {e}")
            # 更新执行状态为失败
            if 'execution' in locals():
                await aitestrebortTestExecution.filter(id=execution.id).update(
                    status="failed",
                    completed_at=datetime.now()
                )
            raise
    
    async def _get_suite_test_cases(self, suite_id: int) -> List[aitestrebortTestCase]:
        """获取测试套件的测试用例"""
        # 通过关联表获取测试用例
        from app.models.aitestrebort.testcase import aitestrebortTestSuiteCase
        
        suite_cases = await aitestrebortTestSuiteCase.filter(suite_id=suite_id).all()
        test_case_ids = [sc.testcase_id for sc in suite_cases]
        
        test_cases = await aitestrebortTestCase.filter(id__in=test_case_ids).all()
        return test_cases
    
    async def _execute_test_cases_concurrent(
        self,
        execution_id: int,
        test_cases: List[aitestrebortTestCase],
        max_concurrent: int
    ) -> List[ExecutionResult]:
        """并发执行测试用例"""
        semaphore = asyncio.Semaphore(max_concurrent)
        tasks = []
        
        for test_case in test_cases:
            task = asyncio.create_task(
                self._execute_single_test_case(semaphore, execution_id, test_case)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ExecutionResult(
                    status=ExecutionStatus.ERROR,
                    error_message=str(result),
                    stack_trace=traceback.format_exc()
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_single_test_case(
        self,
        semaphore: asyncio.Semaphore,
        execution_id: int,
        test_case: aitestrebortTestCase
    ) -> ExecutionResult:
        """执行单个测试用例"""
        async with semaphore:
            start_time = datetime.now()
            
            try:
                # 创建测试用例结果记录
                result_record = await aitestrebortTestCaseResult.create(
                    execution_id=execution_id,
                    testcase_id=test_case.id,
                    status="running",
                    started_at=start_time
                )
                
                await self._notify_callbacks("testcase_started", {
                    "execution_id": execution_id,
                    "testcase_id": test_case.id,
                    "testcase_name": test_case.name
                })
                
                # 检查是否有自动化脚本
                automation_scripts = await aitestrebortAutomationScript.filter(
                    test_case_id=test_case.id,
                    status="active"
                ).all()
                
                if automation_scripts:
                    # 执行自动化脚本
                    result = await self._execute_automation_script(
                        automation_scripts[0], execution_id
                    )
                else:
                    # 执行手动测试用例
                    result = await self._execute_manual_test_case(test_case)
                
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                # 更新结果记录
                await aitestrebortTestCaseResult.filter(id=result_record.id).update(
                    status=result.status.value,
                    completed_at=end_time,
                    execution_time=execution_time,
                    error_message=result.error_message,
                    stack_trace=result.stack_trace,
                    screenshots=result.screenshots,
                    execution_log="\n".join(result.logs)
                )
                
                result.execution_time = execution_time
                
                await self._notify_callbacks("testcase_completed", {
                    "execution_id": execution_id,
                    "testcase_id": test_case.id,
                    "testcase_name": test_case.name,
                    "status": result.status.value,
                    "execution_time": execution_time
                })
                
                return result
                
            except Exception as e:
                logger.error(f"Test case execution failed: {e}")
                
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                error_result = ExecutionResult(
                    status=ExecutionStatus.ERROR,
                    error_message=str(e),
                    stack_trace=traceback.format_exc(),
                    execution_time=execution_time
                )
                
                # 更新结果记录
                if 'result_record' in locals():
                    await aitestrebortTestCaseResult.filter(id=result_record.id).update(
                        status="error",
                        completed_at=end_time,
                        execution_time=execution_time,
                        error_message=str(e),
                        stack_trace=traceback.format_exc()
                    )
                
                return error_result
    
    async def _execute_automation_script(
        self,
        script: aitestrebortAutomationScript,
        execution_id: int
    ) -> ExecutionResult:
        """执行自动化脚本"""
        try:
            # 创建脚本执行记录
            script_execution = await aitestrebortScriptExecution.create(
                script_id=script.id,
                test_execution_id=execution_id,
                executor_id=1,  # TODO: 从上下文获取
                status="running",
                started_at=datetime.now()
            )
            
            # 根据脚本类型执行
            if script.script_type == "playwright_python":
                result = await self._execute_playwright_script(script)
            else:
                result = ExecutionResult(
                    status=ExecutionStatus.SKIPPED,
                    message=f"Unsupported script type: {script.script_type}"
                )
            
            # 更新脚本执行记录
            await aitestrebortScriptExecution.filter(id=script_execution.id).update(
                status=result.status.value,
                completed_at=datetime.now(),
                output=result.message,
                error_message=result.error_message,
                stack_trace=result.stack_trace,
                screenshots=result.screenshots
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Automation script execution failed: {e}")
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            )
    
    async def _execute_playwright_script(
        self,
        script: aitestrebortAutomationScript
    ) -> ExecutionResult:
        """执行Playwright脚本"""
        try:
            from ..tools.playwright_runner import PlaywrightRunner
            
            runner = PlaywrightRunner()
            result = await runner.execute_script(
                script.script_content,
                target_url=script.target_url,
                timeout=script.timeout_seconds,
                headless=script.headless
            )
            
            return ExecutionResult(
                status=ExecutionStatus.PASS if result["success"] else ExecutionStatus.FAIL,
                message=result.get("message", ""),
                error_message=result.get("error", ""),
                screenshots=result.get("screenshots", []),
                logs=result.get("logs", []),
                metadata=result.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Playwright script execution failed: {e}")
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            )
    
    async def _execute_manual_test_case(
        self,
        test_case: aitestrebortTestCase
    ) -> ExecutionResult:
        """执行手动测试用例（模拟）"""
        try:
            # 模拟手动测试执行
            await asyncio.sleep(1)  # 模拟执行时间
            
            # 这里可以集成其他测试工具或人工确认流程
            # 目前返回模拟结果
            
            return ExecutionResult(
                status=ExecutionStatus.PASS,
                message=f"Manual test case '{test_case.name}' executed successfully",
                logs=[
                    f"Started manual test case: {test_case.name}",
                    f"Description: {test_case.description}",
                    "Manual execution completed"
                ]
            )
            
        except Exception as e:
            logger.error(f"Manual test case execution failed: {e}")
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            )
    
    def _calculate_execution_stats(self, results: List[ExecutionResult]) -> Dict[str, int]:
        """计算执行统计"""
        stats = {
            "total": len(results),
            "passed": 0,
            "failed": 0,
            "error": 0,
            "skipped": 0,
            "cancelled": 0
        }
        
        for result in results:
            if result.status == ExecutionStatus.PASS:
                stats["passed"] += 1
            elif result.status == ExecutionStatus.FAIL:
                stats["failed"] += 1
            elif result.status == ExecutionStatus.ERROR:
                stats["error"] += 1
            elif result.status == ExecutionStatus.SKIPPED:
                stats["skipped"] += 1
            elif result.status == ExecutionStatus.CANCELLED:
                stats["cancelled"] += 1
        
        return stats
    
    async def cancel_execution(self, execution_id: int) -> bool:
        """取消执行"""
        try:
            # 更新执行状态
            await aitestrebortTestExecution.filter(id=execution_id).update(
                status="cancelled",
                completed_at=datetime.now()
            )
            
            # 取消相关的测试用例结果
            await aitestrebortTestCaseResult.filter(
                execution_id=execution_id,
                status="running"
            ).update(
                status="cancelled",
                completed_at=datetime.now()
            )
            
            await self._notify_callbacks("execution_cancelled", {
                "execution_id": execution_id
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Cancel execution failed: {e}")
            return False
    
    async def get_execution_progress(self, execution_id: int) -> Dict[str, Any]:
        """获取执行进度"""
        try:
            execution = await aitestrebortTestExecution.get_or_none(id=execution_id)
            if not execution:
                return {}
            
            # 获取测试用例结果统计
            results = await aitestrebortTestCaseResult.filter(execution_id=execution_id).all()
            
            stats = {
                "total": execution.total_count,
                "completed": len([r for r in results if r.status in ["pass", "fail", "error", "skipped"]]),
                "running": len([r for r in results if r.status == "running"]),
                "passed": len([r for r in results if r.status == "pass"]),
                "failed": len([r for r in results if r.status == "fail"]),
                "error": len([r for r in results if r.status == "error"]),
                "skipped": len([r for r in results if r.status == "skipped"])
            }
            
            progress = (stats["completed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            
            return {
                "execution_id": execution_id,
                "status": execution.status,
                "progress": round(progress, 2),
                "stats": stats,
                "started_at": execution.started_at.isoformat() if execution.started_at else None,
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None
            }
            
        except Exception as e:
            logger.error(f"Get execution progress failed: {e}")
            return {}
    
    async def cleanup(self):
        """清理资源"""
        self.executor.shutdown(wait=True)
        
        # 取消所有运行中的任务
        for task in self.running_tasks.values():
            if not task.done():
                task.cancel()
        
        self.running_tasks.clear()


# 全局测试执行器实例
_test_executor = None


def get_test_executor() -> TestExecutor:
    """获取测试执行器实例"""
    global _test_executor
    if _test_executor is None:
        _test_executor = TestExecutor()
    return _test_executor


async def cleanup_test_executor():
    """清理测试执行器"""
    global _test_executor
    if _test_executor:
        await _test_executor.cleanup()
        _test_executor = None