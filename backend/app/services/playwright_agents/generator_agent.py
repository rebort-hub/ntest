"""
Generator Agent - 代码生成器
"""
import logging
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


class GeneratorAgent:
    """代码生成器Agent - 直接使用 Playwright"""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
    
    async def generate_test_code(
        self,
        test_plan: Dict[str, Any],
        framework: str = "playwright",
        language: str = "typescript"
    ) -> Dict[str, Any]:
        """
        生成测试代码
        基于真实页面结构生成更准确的 Playwright 代码
        
        Args:
            test_plan: 测试计划数据（包含页面快照）
            framework: 测试框架
            language: 编程语言
            
        Returns:
            生成的代码和配置
        """
        try:
            logger.info(f"开始生成测试代码: {framework} ({language})")
            
            # 获取页面快照信息（如果有的话）
            snapshot = test_plan.get('exploration_result', {}).get('snapshot', {})
            
            # 构建增强的代码生成提示词
            prompt = self._build_enhanced_generation_prompt(
                test_plan, snapshot, framework, language
            )
            
            # 调用LLM生成代码
            logger.info("调用 LLM 生成代码...")
            response = await self.llm_service.generate_text(
                prompt=prompt,
                temperature=0.2,  # 较低温度确保代码质量
                max_tokens=4000
            )
            
            # 检查响应是否为错误
            if isinstance(response, dict) and response.get('status') in ['434', '400', '500']:
                error_msg = response.get('msg', '未知错误')
                logger.error(f"LLM 调用失败: {error_msg}")
                raise Exception(f"LLM 调用失败: {error_msg}")
            
            if not response or not isinstance(response, str):
                logger.error(f"LLM 返回无效响应: {response}")
                raise Exception(f"LLM 返回无效响应")
            
            logger.info(f"LLM 响应长度: {len(response)} 字符")
            
            # 解析生成的代码
            code, config = self._parse_generated_code(response, language)
            
            if not code or len(code) < 50:
                logger.error(f"生成的代码太短或为空: {code[:100]}")
                raise Exception("生成的代码无效或太短")
            
            # 如果有页面快照，优化选择器
            if snapshot and not snapshot.get('error'):
                code = self._optimize_selectors(code, snapshot, language)
            
            result = {
                "code": code,
                "config_file": config,
                "framework": framework,
                "language": language,
                "enhanced": bool(snapshot and not snapshot.get('error'))
            }
            
            logger.info("✓ 代码生成完成")
            return result
            
        except Exception as e:
            logger.error(f"代码生成失败: {str(e)}", exc_info=True)
            raise
    
    def _build_enhanced_generation_prompt(
        self,
        test_plan: Dict[str, Any],
        snapshot: Dict[str, Any],
        framework: str,
        language: str
    ) -> str:
        """构建增强的代码生成提示词"""
        
        url = test_plan.get('url', '')
        scenarios = test_plan.get('test_scenarios', [])
        
        # 构建场景文本
        scenarios_text = ""
        for idx, scenario in enumerate(scenarios, 1):
            scenarios_text += f"\n场景 {idx}: {scenario.get('name', '未命名场景')}\n"
            scenarios_text += f"描述: {scenario.get('description', '')}\n"
            scenarios_text += f"优先级: {scenario.get('priority', 'medium')}\n"
            scenarios_text += "步骤:\n"
            for step_idx, step in enumerate(scenario.get('steps', []), 1):
                scenarios_text += f"  {step_idx}. {step}\n"
            scenarios_text += f"预期结果: {scenario.get('expected_result', '')}\n"
        
        # 构建页面结构信息
        page_info = ""
        if snapshot and not snapshot.get('error'):
            page_info = f"\n\n## 真实页面结构信息\n"
            page_info += f"页面标题: {snapshot.get('title', '')}\n"
            page_info += f"页面URL: {snapshot.get('url', '')}\n"
            
            if snapshot.get('links'):
                page_info += f"\n可用链接 ({len(snapshot['links'])}个):\n"
                for link in snapshot['links'][:10]:
                    page_info += f"  - \"{link.get('text', '')}\": {link.get('href', '')}\n"
            
            if snapshot.get('buttons'):
                page_info += f"\n可用按钮 ({len(snapshot['buttons'])}个):\n"
                for btn in snapshot['buttons'][:10]:
                    page_info += f"  - \"{btn.get('text', '')}\": {btn.get('type', 'button')}\n"
            
            if snapshot.get('inputs'):
                page_info += f"\n输入框 ({len(snapshot['inputs'])}个):\n"
                for inp in snapshot['inputs'][:10]:
                    page_info += f"  - {inp.get('type', 'text')}: name=\"{inp.get('name', '')}\", placeholder=\"{inp.get('placeholder', '')}\"\n"
            
            if snapshot.get('forms'):
                page_info += f"\n表单 ({len(snapshot['forms'])}个):\n"
                for form in snapshot['forms'][:5]:
                    page_info += f"  - action=\"{form.get('action', '')}\", method={form.get('method', 'GET')}, inputs={form.get('inputs', 0)}\n"
        
        if language == "typescript":
            return self._build_typescript_prompt(url, scenarios_text, page_info)
        elif language == "python":
            return self._build_python_prompt(url, scenarios_text, page_info)
        else:
            return self._build_javascript_prompt(url, scenarios_text, page_info)
    
    def _build_typescript_prompt(self, url: str, scenarios_text: str, page_info: str) -> str:
        """构建增强的 TypeScript 代码生成提示词"""
        return f"""
你是一个专业的测试工程师，需要为以下测试计划生成高质量的 Playwright TypeScript 测试代码。

应用URL: {url}

测试场景:
{scenarios_text}
{page_info}

请生成完整的 Playwright TypeScript 测试代码，要求：
1. 使用 @playwright/test 框架
2. 每个测试场景对应一个 test() 函数
3. 基于真实页面结构使用准确的选择器
4. 包含详细的断言验证
5. 添加适当的等待和错误处理
6. 使用 page.getByRole(), page.getByText() 等现代选择器
7. 添加有意义的测试描述和注释
8. 代码应该是可直接运行的

请按以下格式返回：

```typescript
// 测试代码
import {{ test, expect }} from '@playwright/test';

test.describe('{url} 自动化测试', () => {{
  test.beforeEach(async ({{ page }}) => {{
    await page.goto('{url}');
  }});

  test('场景1测试', async ({{ page }}) => {{
    // 详细的测试步骤
  }});
}});
```

```json
// playwright.config.ts 配置
{{
  "use": {{
    "baseURL": "{url}",
    "screenshot": "only-on-failure",
    "video": "retain-on-failure"
  }}
}}
```

请确保生成的代码质量高、可维护性强。
"""
    
    def _build_python_prompt(self, url: str, scenarios_text: str, page_info: str) -> str:
        """构建增强的 Python 代码生成提示词"""
        return f"""
你是一个专业的测试工程师，需要为以下测试计划生成高质量的 Playwright Python 测试代码。

应用URL: {url}

测试场景:
{scenarios_text}
{page_info}

请生成完整的 Playwright Python 测试代码，要求：
1. 使用 pytest 和 playwright
2. 每个测试场景对应一个 test_ 函数
3. 基于真实页面结构使用准确的选择器
4. 使用 expect() 进行断言
5. 添加适当的等待和错误处理
6. 使用现代的 Playwright Python API
7. 代码应该是可直接运行的

请按以下格式返回：

```python
# 测试代码
import pytest
from playwright.sync_api import Page, expect

def test_scenario_1(page: Page):
    \"\"\"场景1测试\"\"\"
    page.goto('{url}')
    # 测试步骤
    pass
```

```json
// pytest.ini 配置
{{
  "base_url": "{url}"
}}
```
"""
    
    def _build_javascript_prompt(self, url: str, scenarios_text: str, page_info: str) -> str:
        """构建增强的 JavaScript 代码生成提示词"""
        return f"""
你是一个专业的测试工程师，需要为以下测试计划生成高质量的 Playwright JavaScript 测试代码。

应用URL: {url}

测试场景:
{scenarios_text}
{page_info}

请生成完整的 Playwright JavaScript 测试代码，要求：
1. 使用 @playwright/test 框架
2. 每个测试场景对应一个 test() 函数
3. 基于真实页面结构使用准确的选择器
4. 包含详细的断言验证
5. 添加适当的等待和错误处理
6. 代码应该是可直接运行的

请按以下格式返回：

```javascript
// 测试代码
const {{ test, expect }} = require('@playwright/test');

test.describe('{url} 自动化测试', () => {{
  test.beforeEach(async ({{ page }}) => {{
    await page.goto('{url}');
  }});

  test('场景1测试', async ({{ page }}) => {{
    // 测试步骤
  }});
}});
```

```json
// playwright.config.js 配置
{{
  "use": {{
    "baseURL": "{url}"
  }}
}}
```
"""
    
    def _optimize_selectors(self, code: str, snapshot: Dict[str, Any], language: str) -> str:
        """基于页面快照优化选择器"""
        try:
            # 简单的选择器优化：将通用选择器替换为更具体的
            optimized_code = code
            
            # 优化按钮选择器
            if snapshot.get('buttons'):
                for btn in snapshot['buttons'][:5]:
                    btn_text = btn.get('text', '').strip()
                    if btn_text:
                        # 将通用的按钮选择器替换为具体的文本选择器
                        if language in ['typescript', 'javascript']:
                            optimized_code = optimized_code.replace(
                                'button',
                                f'button:has-text("{btn_text}")',
                                1  # 只替换第一个
                            )
                        elif language == 'python':
                            optimized_code = optimized_code.replace(
                                '"button"',
                                f'"button:has-text(\'{btn_text}\')"',
                                1
                            )
            
            # 优化链接选择器
            if snapshot.get('links'):
                for link in snapshot['links'][:5]:
                    link_text = link.get('text', '').strip()
                    if link_text:
                        if language in ['typescript', 'javascript']:
                            optimized_code = optimized_code.replace(
                                'a',
                                f'a:has-text("{link_text}")',
                                1
                            )
                        elif language == 'python':
                            optimized_code = optimized_code.replace(
                                '"a"',
                                f'"a:has-text(\'{link_text}\')"',
                                1
                            )
            
            return optimized_code
            
        except Exception as e:
            logger.warning(f"选择器优化失败: {str(e)}")
            return code
    
    def _parse_generated_code(self, response: str, language: str) -> tuple:
        """解析生成的代码"""
        import re
        
        # 提取代码块
        code_pattern = r'```(?:typescript|python|javascript)?\n?([\s\S]*?)```'
        matches = re.findall(code_pattern, response)
        
        code = ""
        config = ""
        
        if len(matches) >= 1:
            code = matches[0].strip()
        
        if len(matches) >= 2:
            config = matches[1].strip()
        
        # 如果没有找到代码块，返回整个响应
        if not code:
            code = response.strip()
        
        return code, config
