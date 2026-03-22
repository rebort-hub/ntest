"""
Playwright代码生成器，从测试用例生成Playwright自动化脚本
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PlaywrightCodeGenerator:
    """Playwright代码生成器"""
    
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
    
    async def generate_from_test_case(
        self,
        test_case_name: str,
        test_case_description: str,
        test_steps: List[Dict[str, Any]],
        target_url: str = "https://example.com",
        language: str = "python"
    ) -> str:
        """
        从测试用例生成Playwright脚本
        
        Args:
            test_case_name: 测试用例名称
            test_case_description: 测试用例描述
            test_steps: 测试步骤列表
            target_url: 目标URL
            language: 编程语言 (python/javascript)
        
        Returns:
            生成的Playwright脚本代码
        """
        try:
            if self.llm_service:
                # 使用AI生成
                return await self._generate_with_ai(
                    test_case_name, test_case_description, test_steps, target_url, language
                )
            else:
                # 使用规则生成
                return self._generate_with_rules(
                    test_case_name, test_case_description, test_steps, target_url, language
                )
        except Exception as e:
            logger.error(f"生成脚本失败: {str(e)}", exc_info=True)
            # 如果AI生成失败，降级到规则生成
            return self._generate_with_rules(
                test_case_name, test_case_description, test_steps, target_url, language
            )
    
    async def _generate_with_ai(
        self,
        test_case_name: str,
        test_case_description: str,
        test_steps: List[Dict[str, Any]],
        target_url: str,
        language: str
    ) -> str:
        """使用AI生成Playwright脚本"""
        
        # 构建提示词
        steps_text = "\n".join([
            f"{step['step_number']}. {step['description']} (期望结果: {step['expected_result']})"
            for step in test_steps
        ])
        
        prompt = f"""
请根据以下测试用例信息生成一个完整的Playwright自动化测试脚本：

测试用例名称: {test_case_name}
测试用例描述: {test_case_description}
目标URL: {target_url}
编程语言: {language}

测试步骤:
{steps_text}

要求:
1. 生成完整可执行的Playwright脚本
2. 包含必要的导入和设置
3. 使用{'pytest框架' if language == 'python' else 'Jest框架'}
4. 添加适当的等待和断言
5. 包含错误处理
6. 代码要清晰易读，有适当的注释

请直接返回代码，不要包含其他解释文字。
"""
        
        try:
            # 调用LLM生成代码
            response = await self.llm_service.generate_text(prompt, temperature=0.3, max_tokens=2000)
            
            # 清理响应，提取代码部分
            code = self._extract_code_from_response(response, language)
            
            logger.info(f"AI生成脚本成功: {test_case_name}")
            return code
            
        except Exception as e:
            logger.error(f"AI生成失败: {str(e)}")
            raise e
    
    def _generate_with_rules(
        self,
        test_case_name: str,
        test_case_description: str,
        test_steps: List[Dict[str, Any]],
        target_url: str,
        language: str
    ) -> str:
        """使用规则生成Playwright脚本"""
        
        if language == "python":
            return self._generate_python_script(
                test_case_name, test_case_description, test_steps, target_url
            )
        else:
            return self._generate_javascript_script(
                test_case_name, test_case_description, test_steps, target_url
            )
    
    def _generate_python_script(
        self,
        test_case_name: str,
        test_case_description: str,
        test_steps: List[Dict[str, Any]],
        target_url: str
    ) -> str:
        """生成Python Playwright脚本"""
        
        # 清理类名和方法名
        class_name = self._sanitize_name(test_case_name, capitalize=True)
        method_name = self._sanitize_name(test_case_name, capitalize=False)
        
        # 生成测试步骤代码
        steps_code = []
        for step in test_steps:
            step_comment = f"        # 步骤 {step['step_number']}: {step['description']}"
            step_code = f"        # TODO: 实现步骤 - {step['description']}"
            step_assertion = f"        # 验证: {step['expected_result']}"
            
            steps_code.extend([step_comment, step_code, step_assertion, ""])
        
        steps_code_str = "\n".join(steps_code)
        
        template = f'''"""
{test_case_name} - Playwright自动化测试脚本
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
测试描述: {test_case_description}
目标URL: {target_url}
"""
import pytest
from playwright.async_api import async_playwright, Page, Browser, BrowserContext


class Test{class_name}:
    """测试类: {test_case_name}"""
    
    @pytest.mark.asyncio
    async def test_{method_name}(self):
        """
        测试方法: {test_case_name}
        描述: {test_case_description}
        """
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # 导航到目标页面
                await page.goto("{target_url}")
                await page.wait_for_load_state("networkidle")
                
{steps_code_str}
                
                print(f"✅ 测试用例 '{test_case_name}' 执行完成")
                
            except Exception as e:
                print(f"❌ 测试用例 '{test_case_name}' 执行失败: {{str(e)}}")
                raise e
            finally:
                # 清理资源
                await context.close()
                await browser.close()


if __name__ == "__main__":
    # 单独运行此脚本
    import asyncio
    
    async def run_test():
        test_instance = Test{class_name}()
        await test_instance.test_{method_name}()
    
    asyncio.run(run_test())
'''
        
        return template
    
    def _generate_javascript_script(
        self,
        test_case_name: str,
        test_case_description: str,
        test_steps: List[Dict[str, Any]],
        target_url: str
    ) -> str:
        """生成JavaScript Playwright脚本"""
        
        method_name = self._sanitize_name(test_case_name, capitalize=False)
        
        # 生成测试步骤代码
        steps_code = []
        for step in test_steps:
            step_comment = f"    // 步骤 {step['step_number']}: {step['description']}"
            step_code = f"    // TODO: 实现步骤 - {step['description']}"
            step_assertion = f"    // 验证: {step['expected_result']}"
            
            steps_code.extend([step_comment, step_code, step_assertion, ""])
        
        steps_code_str = "\n".join(steps_code)
        
        template = f'''/**
 * {test_case_name} - Playwright自动化测试脚本
 * 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 * 测试描述: {test_case_description}
 * 目标URL: {target_url}
 */
const {{ test, expect }} = require('@playwright/test');

test.describe('{test_case_name}', () => {{
  test('{method_name}', async ({{ page }}) => {{
    try {{
      // 导航到目标页面
      await page.goto('{target_url}');
      await page.waitForLoadState('networkidle');
      
{steps_code_str}
      
      console.log('✅ 测试用例 "{test_case_name}" 执行完成');
      
    }} catch (error) {{
      console.error('❌ 测试用例 "{test_case_name}" 执行失败:', error);
      throw error;
    }}
  }});
}});
'''
        
        return template
    
    def _sanitize_name(self, name: str, capitalize: bool = False) -> str:
        """清理名称，使其符合变量命名规范"""
        import re
        # 移除特殊字符，只保留字母数字和下划线
        sanitized = re.sub(r'[^\w\u4e00-\u9fff]', '_', name)
        # 移除连续的下划线
        sanitized = re.sub(r'_+', '_', sanitized)
        # 移除开头和结尾的下划线
        sanitized = sanitized.strip('_')
        
        if capitalize:
            return sanitized.title().replace('_', '')
        else:
            return sanitized.lower()
    
    def _extract_code_from_response(self, response: str, language: str) -> str:
        """从LLM响应中提取代码"""
        import re
        
        # 尝试提取代码块
        if language == "python":
            pattern = r'```python\n(.*?)\n```'
        else:
            pattern = r'```(?:javascript|js|typescript|ts)\n(.*?)\n```'
        
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # 如果没有找到代码块，返回整个响应
        return response.strip()