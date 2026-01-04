"""
脚本生成引擎
基于测试用例和Agent步骤生成自动化脚本
"""
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

from app.models.aitestrebort.testcase import aitestrebortTestCase, aitestrebortTestCaseStep
from app.models.aitestrebort.automation import aitestrebortAutomationScript
from app.models.aitestrebort.orchestrator import AgentStep
from app.services.ai.llm_service import get_llm_service
from app.services.ai.prompt_manager import PromptType, format_prompt

logger = logging.getLogger(__name__)


class ScriptType(str, Enum):
    """脚本类型"""
    PLAYWRIGHT_PYTHON = "playwright_python"
    PLAYWRIGHT_JAVASCRIPT = "playwright_javascript"
    SELENIUM_PYTHON = "selenium_python"
    CYPRESS = "cypress"


class ScriptTemplate:
    """脚本模板"""
    
    PLAYWRIGHT_PYTHON_TEMPLATE = '''
import asyncio
from playwright.async_api import async_playwright, Page, Browser
import pytest
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class {class_name}:
    """
    {test_description}
    """
    
    def __init__(self, page: Page):
        self.page = page
        self.timeout = {timeout} * 1000  # 转换为毫秒
        
        # 页面元素定位器
{element_locators}
    
    async def setup(self):
        """测试前置条件"""
        try:
{setup_steps}
        except Exception as e:
            logger.error(f"Setup failed: {{e}}")
            raise
    
    async def execute_test(self):
        """执行测试步骤"""
        try:
{test_steps}
        except Exception as e:
            logger.error(f"Test execution failed: {{e}}")
            raise
    
    async def verify_results(self):
        """验证测试结果"""
        try:
{verification_steps}
        except Exception as e:
            logger.error(f"Result verification failed: {{e}}")
            raise
    
    async def cleanup(self):
        """测试清理"""
        try:
{cleanup_steps}
        except Exception as e:
            logger.warning(f"Cleanup failed: {{e}}")


async def test_{method_name}():
    """
    测试用例：{test_name}
    描述：{test_description}
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless={headless},
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        try:
            page = await browser.new_page()
            
            # 设置视口大小
            await page.set_viewport_size({{"width": 1920, "height": 1080}})
            
            # 创建测试实例
            test_instance = {class_name}(page)
            
            # 执行测试流程
            await test_instance.setup()
            await test_instance.execute_test()
            await test_instance.verify_results()
            await test_instance.cleanup()
            
            logger.info("测试执行成功")
            
        except Exception as e:
            logger.error(f"测试执行失败: {{e}}")
            # 截图保存错误现场
            try:
                await page.screenshot(path=f"error_screenshot_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.png")
            except:
                pass
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_{method_name}())
'''

    PLAYWRIGHT_JAVASCRIPT_TEMPLATE = '''
const {{ test, expect }} = require('@playwright/test');

test.describe('{test_name}', () => {{
    test('{test_description}', async ({{ page }}) => {{
        // 设置超时时间
        test.setTimeout({timeout} * 1000);
        
        try {{
            // 前置条件
{setup_steps}
            
            // 执行测试步骤
{test_steps}
            
            // 验证结果
{verification_steps}
            
        }} catch (error) {{
            console.error('测试执行失败:', error);
            // 截图保存错误现场
            await page.screenshot({{ path: `error_screenshot_${{Date.now()}}.png` }});
            throw error;
        }}
    }});
}});
'''


class ScriptGenerator:
    """脚本生成器"""
    
    def __init__(self):
        self.llm_service = None
    
    async def _get_llm_service(self):
        """获取LLM服务"""
        if self.llm_service is None:
            self.llm_service = await get_llm_service()
        return self.llm_service
    
    async def generate_from_test_case(
        self,
        test_case: aitestrebortTestCase,
        script_type: ScriptType = ScriptType.PLAYWRIGHT_PYTHON,
        target_url: Optional[str] = None,
        timeout: int = 30,
        headless: bool = True
    ) -> str:
        """从测试用例生成脚本"""
        try:
            # 获取测试步骤
            steps = await aitestrebortTestCaseStep.filter(
                test_case_id=test_case.id
            ).order_by('step_number').all()
            
            # 构建测试步骤文本
            test_steps_text = []
            for step in steps:
                test_steps_text.append(f"{step.step_number}. {step.description}")
                test_steps_text.append(f"   预期结果: {step.expected_result}")
            
            # 使用LLM生成脚本
            llm_service = await self._get_llm_service()
            
            # 准备提示词参数
            prompt_params = {
                "test_case_name": test_case.name,
                "test_case_description": test_case.description or "",
                "precondition": test_case.precondition or "无特殊前置条件",
                "test_steps": "\n".join(test_steps_text),
                "expected_result": "所有步骤按预期执行完成",
                "target_url": target_url or "https://example.com",
                "test_class_name": self._generate_class_name(test_case.name),
                "test_method_name": self._generate_method_name(test_case.name)
            }
            
            # 生成脚本
            if script_type == ScriptType.PLAYWRIGHT_PYTHON:
                script_content = await self._generate_playwright_python_script(
                    prompt_params, timeout, headless
                )
            elif script_type == ScriptType.PLAYWRIGHT_JAVASCRIPT:
                script_content = await self._generate_playwright_javascript_script(
                    prompt_params, timeout
                )
            else:
                raise ValueError(f"Unsupported script type: {script_type}")
            
            return script_content
            
        except Exception as e:
            logger.error(f"Generate script from test case failed: {e}")
            raise
    
    async def generate_from_agent_steps(
        self,
        agent_steps: List[AgentStep],
        script_type: ScriptType = ScriptType.PLAYWRIGHT_PYTHON,
        target_url: Optional[str] = None,
        timeout: int = 30,
        headless: bool = True
    ) -> str:
        """从Agent步骤生成脚本"""
        try:
            # 分析Agent步骤，提取操作信息
            operations = []
            for step in agent_steps:
                if step.tool_name and "playwright" in step.tool_name.lower():
                    # 解析Playwright操作
                    operation = self._parse_playwright_operation(step)
                    if operation:
                        operations.append(operation)
            
            if not operations:
                raise ValueError("No valid Playwright operations found in agent steps")
            
            # 生成脚本
            script_content = await self._generate_script_from_operations(
                operations, script_type, target_url, timeout, headless
            )
            
            return script_content
            
        except Exception as e:
            logger.error(f"Generate script from agent steps failed: {e}")
            raise
    
    def _parse_playwright_operation(self, step: AgentStep) -> Optional[Dict[str, Any]]:
        """解析Playwright操作"""
        try:
            if not step.tool_input:
                return None
            
            # 尝试解析工具输入
            tool_input = step.tool_input
            if isinstance(tool_input, str):
                import json
                tool_input = json.loads(tool_input)
            
            operation = {
                "action": tool_input.get("action", "unknown"),
                "selector": tool_input.get("selector", ""),
                "value": tool_input.get("value", ""),
                "description": step.ai_response or "",
                "step_number": step.step_number
            }
            
            return operation
            
        except Exception as e:
            logger.warning(f"Failed to parse Playwright operation: {e}")
            return None
    
    async def _generate_script_from_operations(
        self,
        operations: List[Dict[str, Any]],
        script_type: ScriptType,
        target_url: Optional[str],
        timeout: int,
        headless: bool
    ) -> str:
        """从操作列表生成脚本"""
        try:
            # 构建操作描述
            operations_text = []
            for op in operations:
                operations_text.append(
                    f"步骤{op['step_number']}: {op['action']} - {op['description']}"
                )
            
            # 使用LLM生成脚本
            llm_service = await self._get_llm_service()
            
            prompt = f"""
基于以下Playwright操作记录，生成完整的自动化测试脚本：

操作记录：
{chr(10).join(operations_text)}

目标URL: {target_url or 'https://example.com'}
脚本类型: {script_type.value}
超时时间: {timeout}秒
无头模式: {headless}

请生成完整可执行的{script_type.value}脚本，包含：
1. 必要的导入和设置
2. 页面操作的具体实现
3. 适当的等待和异常处理
4. 结果验证
"""
            
            script_content = await llm_service.generate_text(prompt, temperature=0.3)
            return script_content
            
        except Exception as e:
            logger.error(f"Generate script from operations failed: {e}")
            raise
    
    async def _generate_playwright_python_script(
        self,
        params: Dict[str, Any],
        timeout: int,
        headless: bool
    ) -> str:
        """生成Playwright Python脚本"""
        try:
            llm_service = await self._get_llm_service()
            
            # 使用提示词模板
            script_content = await llm_service.generate_playwright_script({
                "name": params["test_case_name"],
                "description": params["test_case_description"],
                "precondition": params["precondition"],
                "steps": params["test_steps"].split("\n"),
                "expected_result": params["expected_result"]
            })
            
            return script_content
            
        except Exception as e:
            logger.error(f"Generate Playwright Python script failed: {e}")
            # 返回基础模板
            return self._generate_basic_playwright_script(params, timeout, headless)
    
    async def _generate_playwright_javascript_script(
        self,
        params: Dict[str, Any],
        timeout: int
    ) -> str:
        """生成Playwright JavaScript脚本"""
        try:
            # 构建基础JavaScript脚本
            setup_steps = "            await page.goto('{}');".format(
                params.get("target_url", "https://example.com")
            )
            
            test_steps = "            // TODO: 实现具体的测试步骤\n"
            test_steps += "            await page.waitForLoadState('networkidle');"
            
            verification_steps = "            // TODO: 添加结果验证\n"
            verification_steps += "            await expect(page).toHaveTitle(/.+/);"
            
            script_content = ScriptTemplate.PLAYWRIGHT_JAVASCRIPT_TEMPLATE.format(
                test_name=params["test_case_name"],
                test_description=params["test_case_description"],
                timeout=timeout,
                setup_steps=setup_steps,
                test_steps=test_steps,
                verification_steps=verification_steps
            )
            
            return script_content
            
        except Exception as e:
            logger.error(f"Generate Playwright JavaScript script failed: {e}")
            raise
    
    def _generate_basic_playwright_script(
        self,
        params: Dict[str, Any],
        timeout: int,
        headless: bool
    ) -> str:
        """生成基础Playwright脚本"""
        class_name = params.get("test_class_name", "TestCase")
        method_name = params.get("test_method_name", "test_example")
        
        # 构建脚本内容
        element_locators = "        # TODO: 定义页面元素定位器"
        setup_steps = f"            await self.page.goto('{params.get('target_url', 'https://example.com')}')"
        test_steps = "            # TODO: 实现具体的测试步骤\n            await self.page.wait_for_load_state('networkidle')"
        verification_steps = "            # TODO: 添加结果验证\n            assert await self.page.title() != ''"
        cleanup_steps = "            # TODO: 清理操作"
        
        script_content = ScriptTemplate.PLAYWRIGHT_PYTHON_TEMPLATE.format(
            class_name=class_name,
            test_description=params.get("test_case_description", "自动生成的测试用例"),
            timeout=timeout,
            element_locators=element_locators,
            setup_steps=setup_steps,
            test_steps=test_steps,
            verification_steps=verification_steps,
            cleanup_steps=cleanup_steps,
            method_name=method_name,
            test_name=params.get("test_case_name", "测试用例"),
            headless=str(headless).lower()
        )
        
        return script_content
    
    def _generate_class_name(self, test_case_name: str) -> str:
        """生成类名"""
        # 移除特殊字符，转换为驼峰命名
        clean_name = re.sub(r'[^\w\s]', '', test_case_name)
        words = clean_name.split()
        class_name = ''.join(word.capitalize() for word in words)
        
        if not class_name:
            class_name = "TestCase"
        elif not class_name[0].isupper():
            class_name = class_name.capitalize()
        
        return class_name + "Test"
    
    def _generate_method_name(self, test_case_name: str) -> str:
        """生成方法名"""
        # 移除特殊字符，转换为下划线命名
        clean_name = re.sub(r'[^\w\s]', '', test_case_name)
        words = clean_name.lower().split()
        method_name = '_'.join(words)
        
        if not method_name:
            method_name = "test_case"
        
        return method_name
    
    async def create_automation_script(
        self,
        test_case_id: int,
        script_type: ScriptType = ScriptType.PLAYWRIGHT_PYTHON,
        target_url: Optional[str] = None,
        timeout: int = 30,
        headless: bool = True,
        creator_id: int = 1
    ) -> aitestrebortAutomationScript:
        """创建自动化脚本记录"""
        try:
            # 获取测试用例
            test_case = await aitestrebortTestCase.get_or_none(id=test_case_id)
            if not test_case:
                raise ValueError(f"Test case not found: {test_case_id}")
            
            # 生成脚本内容
            script_content = await self.generate_from_test_case(
                test_case, script_type, target_url, timeout, headless
            )
            
            # 创建脚本记录
            script = await aitestrebortAutomationScript.create(
                test_case_id=test_case_id,
                name=f"{test_case.name}_自动化脚本",
                description=f"基于测试用例'{test_case.name}'自动生成的{script_type.value}脚本",
                script_type=script_type.value,
                source="ai_generated",
                status="active",
                script_content=script_content,
                target_url=target_url,
                timeout_seconds=timeout,
                headless=headless,
                version=1,
                creator_id=creator_id
            )
            
            logger.info(f"Created automation script: {script.id}")
            return script
            
        except Exception as e:
            logger.error(f"Create automation script failed: {e}")
            raise
    
    async def validate_script_syntax(self, script_content: str, script_type: ScriptType) -> Dict[str, Any]:
        """验证脚本语法"""
        try:
            if script_type == ScriptType.PLAYWRIGHT_PYTHON:
                return await self._validate_python_syntax(script_content)
            elif script_type == ScriptType.PLAYWRIGHT_JAVASCRIPT:
                return await self._validate_javascript_syntax(script_content)
            else:
                return {"valid": False, "error": f"Unsupported script type: {script_type}"}
                
        except Exception as e:
            logger.error(f"Script syntax validation failed: {e}")
            return {"valid": False, "error": str(e)}
    
    async def _validate_python_syntax(self, script_content: str) -> Dict[str, Any]:
        """验证Python语法"""
        try:
            import ast
            ast.parse(script_content)
            return {"valid": True, "message": "Python syntax is valid"}
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"Python syntax error: {e.msg}",
                "line": e.lineno,
                "column": e.offset
            }
    
    async def _validate_javascript_syntax(self, script_content: str) -> Dict[str, Any]:
        """验证JavaScript语法（简单检查）"""
        try:
            # 简单的语法检查
            if not script_content.strip():
                return {"valid": False, "error": "Empty script content"}
            
            # 检查基本的JavaScript结构
            required_patterns = [
                r'test\s*\(',  # test函数调用
                r'async\s*\(',  # async函数
                r'await\s+',   # await关键字
            ]
            
            for pattern in required_patterns:
                if not re.search(pattern, script_content):
                    return {
                        "valid": False,
                        "error": f"Missing required pattern: {pattern}"
                    }
            
            return {"valid": True, "message": "JavaScript syntax appears valid"}
            
        except Exception as e:
            return {"valid": False, "error": str(e)}


# 全局脚本生成器实例
_script_generator = None


def get_script_generator() -> ScriptGenerator:
    """获取脚本生成器实例"""
    global _script_generator
    if _script_generator is None:
        _script_generator = ScriptGenerator()
    return _script_generator