"""
aitestrebort 测试执行服务
基于现有的测试执行框架
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TestExecutorService:
    """测试执行服务"""
    
    def __init__(self):
        self.running_executions = {}  # 记录正在运行的执行任务
    
    async def execute_test_suite(
        self,
        suite_id: int,
        execution_id: int,
        max_concurrent: int = 1
    ) -> Dict[str, Any]:
        """
        执行测试套件
        
        Args:
            suite_id: 测试套件ID
            execution_id: 执行记录ID
            max_concurrent: 最大并发数
            
        Returns:
            执行结果
        """
        try:
            from app.models.aitestrebort import (
                aitestrebortTestSuite, aitestrebortTestExecution, 
                aitestrebortTestCaseResult, aitestrebortTestSuiteCase
            )
            
            # 获取测试套件和执行记录
            suite = await aitestrebortTestSuite.get(id=suite_id)
            execution = await aitestrebortTestExecution.get(id=execution_id)
            
            # 更新执行状态
            execution.status = 'running'
            execution.started_at = datetime.now()
            await execution.save()
            
            logger.info(f"开始执行测试套件: {suite.name}")
            
            # 获取所有测试用例
            suite_cases = await aitestrebortTestSuiteCase.filter(suite=suite).all()
            testcases = []
            for suite_case in suite_cases:
                testcase = await suite_case.testcase
                testcases.append(testcase)
            
            execution.total_count = len(testcases)
            await execution.save()
            
            # 创建测试用例结果记录
            for testcase in testcases:
                await aitestrebortTestCaseResult.create(
                    execution=execution,
                    testcase=testcase,
                    status='pending'
                )
            
            # 记录执行任务
            self.running_executions[execution_id] = {
                'suite_id': suite_id,
                'status': 'running',
                'started_at': execution.started_at
            }
            
            # 执行测试用例
            if max_concurrent <= 1:
                # 串行执行
                await self._execute_testcases_serial(testcases, execution)
            else:
                # 并行执行
                await self._execute_testcases_parallel(testcases, execution, max_concurrent)
            
            # 统计执行结果
            await self._update_execution_stats(execution)
            
            # 更新执行状态
            execution.status = 'completed'
            execution.completed_at = datetime.now()
            await execution.save()
            
            # 移除执行记录
            if execution_id in self.running_executions:
                del self.running_executions[execution_id]
            
            logger.info(f"测试套件执行完成: {suite.name}")
            
            return {
                'status': 'completed',
                'total_count': execution.total_count,
                'passed_count': execution.passed_count,
                'failed_count': execution.failed_count,
                'skipped_count': execution.skipped_count,
                'error_count': execution.error_count,
            }
            
        except Exception as e:
            logger.error(f"执行测试套件失败: {str(e)}")
            
            # 更新执行状态为失败
            try:
                from app.models.aitestrebort import aitestrebortTestExecution
                execution = await aitestrebortTestExecution.get(id=execution_id)
                execution.status = 'failed'
                execution.completed_at = datetime.now()
                await execution.save()
                
                # 移除执行记录
                if execution_id in self.running_executions:
                    del self.running_executions[execution_id]
            except:
                pass
            
            raise
    
    async def _execute_testcases_serial(self, testcases: List, execution):
        """串行执行测试用例"""
        for testcase in testcases:
            try:
                await self._execute_single_testcase(testcase, execution)
            except Exception as e:
                logger.error(f"执行测试用例 {testcase.name} 失败: {str(e)}")
    
    async def _execute_testcases_parallel(self, testcases: List, execution, max_concurrent: int):
        """并行执行测试用例"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(testcase):
            async with semaphore:
                try:
                    await self._execute_single_testcase(testcase, execution)
                except Exception as e:
                    logger.error(f"执行测试用例 {testcase.name} 失败: {str(e)}")
        
        # 创建并发任务
        tasks = [execute_with_semaphore(testcase) for testcase in testcases]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_single_testcase(self, testcase, execution):
        """执行单个测试用例"""
        from app.models.aitestrebort import aitestrebortTestCaseResult
        
        try:
            # 获取或创建测试用例结果
            result = await aitestrebortTestCaseResult.filter(
                execution=execution,
                testcase=testcase
            ).first()
            
            if not result:
                result = await aitestrebortTestCaseResult.create(
                    execution=execution,
                    testcase=testcase,
                    status='running'
                )
            else:
                result.status = 'running'
                result.started_at = datetime.now()
                await result.save()
            
            logger.info(f"开始执行测试用例: {testcase.name}")
            
            # 模拟测试执行过程
            execution_log = []
            screenshots = []
            
            # 获取测试步骤
            steps = await testcase.steps.all().order_by("step_number")
            
            for step in steps:
                execution_log.append(f"执行步骤 {step.step_number}: {step.description}")
                
                # 模拟步骤执行
                # 这里应该实现真实的测试步骤执行逻辑
                # 例如：调用 Playwright、Selenium 等自动化工具
                await asyncio.sleep(0.1)  # 模拟执行时间
                
                execution_log.append(f"步骤 {step.step_number} 执行完成")
            
            # 模拟执行结果（实际应该根据真实执行结果判断）
            import random
            success_rate = 0.8  # 80% 成功率
            
            if random.random() < success_rate:
                result.status = 'pass'
                execution_log.append("测试用例执行成功")
            else:
                result.status = 'fail'
                result.error_message = "模拟测试失败"
                execution_log.append("测试用例执行失败")
            
            # 更新结果
            result.completed_at = datetime.now()
            result.execution_log = '\n'.join(execution_log)
            result.screenshots = screenshots
            
            if result.started_at:
                result.execution_time = (
                    result.completed_at - result.started_at
                ).total_seconds()
            
            await result.save()
            
            logger.info(f"测试用例执行完成: {testcase.name}, 结果: {result.status}")
            
        except Exception as e:
            logger.error(f"执行测试用例失败: {str(e)}")
            
            # 更新结果状态为错误
            try:
                result.status = 'error'
                result.error_message = str(e)
                result.completed_at = datetime.now()
                await result.save()
            except:
                pass
            
            raise
    
    async def _update_execution_stats(self, execution):
        """更新执行统计信息"""
        from app.models.aitestrebort import aitestrebortTestCaseResult
        
        # 统计各种状态的用例数量
        results = await aitestrebortTestCaseResult.filter(execution=execution).all()
        
        passed_count = sum(1 for r in results if r.status == 'pass')
        failed_count = sum(1 for r in results if r.status == 'fail')
        skipped_count = sum(1 for r in results if r.status == 'skip')
        error_count = sum(1 for r in results if r.status == 'error')
        
        execution.passed_count = passed_count
        execution.failed_count = failed_count
        execution.skipped_count = skipped_count
        execution.error_count = error_count
        
        await execution.save()
    
    async def cancel_execution(self, execution_id: int) -> bool:
        """取消测试执行"""
        try:
            from app.models.aitestrebort import aitestrebortTestExecution
            
            execution = await aitestrebortTestExecution.get(id=execution_id)
            
            if execution.status in ['pending', 'running']:
                execution.status = 'cancelled'
                execution.completed_at = datetime.now()
                await execution.save()
                
                # 移除执行记录
                if execution_id in self.running_executions:
                    del self.running_executions[execution_id]
                
                logger.info(f"测试执行已取消: {execution_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"取消测试执行失败: {str(e)}")
            return False
    
    def get_running_executions(self) -> Dict[int, Dict[str, Any]]:
        """获取正在运行的执行任务"""
        return self.running_executions.copy()
    
    async def execute_automation_script(
        self,
        script_id: int,
        execution_id: int,
        browser_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行自动化脚本
        
        Args:
            script_id: 脚本ID
            execution_id: 执行记录ID
            browser_config: 浏览器配置
            
        Returns:
            执行结果
        """
        try:
            from app.models.aitestrebort import (
                aitestrebortAutomationScript, aitestrebortScriptExecution
            )
            
            # 获取脚本和执行记录
            script = await aitestrebortAutomationScript.get(id=script_id)
            execution = await aitestrebortScriptExecution.get(id=execution_id)
            
            # 更新执行状态
            execution.status = 'running'
            execution.started_at = datetime.now()
            await execution.save()
            
            logger.info(f"开始执行自动化脚本: {script.name}")
            
            # 模拟脚本执行
            # 这里应该实现真实的脚本执行逻辑
            # 例如：使用 Playwright 执行脚本
            
            await asyncio.sleep(2)  # 模拟执行时间
            
            # 模拟执行结果
            import random
            if random.random() < 0.9:  # 90% 成功率
                execution.status = 'pass'
                execution.output = "脚本执行成功"
            else:
                execution.status = 'fail'
                execution.error_message = "脚本执行失败"
            
            # 更新执行结果
            execution.completed_at = datetime.now()
            if execution.started_at:
                execution.execution_time = (
                    execution.completed_at - execution.started_at
                ).total_seconds()
            
            await execution.save()
            
            logger.info(f"自动化脚本执行完成: {script.name}, 结果: {execution.status}")
            
            return {
                'script_id': script_id,
                'status': execution.status,
                'execution_time': execution.execution_time,
            }
            
        except Exception as e:
            logger.error(f"执行自动化脚本失败: {str(e)}")
            
            # 更新执行状态为错误
            try:
                execution.status = 'error'
                execution.error_message = str(e)
                execution.completed_at = datetime.now()
                await execution.save()
            except:
                pass
            
            raise


# 全局服务实例
test_executor_service = TestExecutorService()