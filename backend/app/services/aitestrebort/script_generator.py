"""
Playwright 脚本生成器

从 Agent 执行的 Playwright MCP 操作步骤生成可重复执行的 Python 脚本
"""
import json
import re
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def convert_js_to_python_playwright(js_code: str) -> Optional[str]:
    """
    将 Playwright JS 代码转换为 Python 代码
    
    示例:
    输入: await page.getByRole('textbox', { name: '请输入用户名' }).fill('admin');
    输出: page.get_by_role('textbox', name='请输入用户名').fill('admin')
    """
    if not js_code or not isinstance(js_code, str):
        return None
    
    code = js_code.strip()
    
    # 移除 await 前缀和末尾分号
    code = re.sub(r'^await\s+', '', code)
    code = re.sub(r';$', '', code)
    
    # 转换方法名：getByRole -> get_by_role, getByText -> get_by_text, etc.
    replacements = [
        ('getByRole', 'get_by_role'),
        ('getByText', 'get_by_text'),
        ('getByLabel', 'get_by_label'),
        ('getByPlaceholder', 'get_by_placeholder'),
        ('getByAltText', 'get_by_alt_text'),
        ('getByTitle', 'get_by_title'),
        ('getByTestId', 'get_by_test_id'),
        ('locator', 'locator'),
        ('waitForTimeout', 'wait_for_timeout'),
        ('waitForSelector', 'wait_for_selector'),
        ('waitForLoadState', 'wait_for_load_state'),
        ('selectOption', 'select_option'),
    ]
    for js_name, py_name in replacements:
        code = code.replace(js_name, py_name)
    
    # 转换 JS 对象字面量为 Python 关键字参数
    # { name: '...' } -> name='...'
    # { name: '...', exact: true } -> name='...', exact=True
    def convert_js_object(match):
        obj_content = match.group(1)
        # 解析简单的 JS 对象
        pairs = []
        # 匹配 key: value 模式
        for pair_match in re.finditer(r"(\w+):\s*('[^']*'|\"[^\"]*\"|true|false|\d+)", obj_content):
            key = pair_match.group(1)
            value = pair_match.group(2)
            # 转换布尔值
            if value == 'true':
                value = 'True'
            elif value == 'false':
                value = 'False'
            pairs.append(f"{key}={value}")
        return ', ' + ', '.join(pairs) if pairs else ''
    
    # 匹配 get_by_role('...', { ... })
    code = re.sub(r",\s*\{\s*([^}]+)\s*\}", convert_js_object, code)
    
    return code


# MCP 工具名到 Playwright 代码的映射
TOOL_MAPPING = {
    'browser_navigate': 'page.goto("{url}")',
    'mcp_chrome-devtoo_navigate': 'page.goto("{url}")',
    'browser_click': 'page.locator("{selector}").click()',
    'mcp_chrome-devtoo_click': 'page.locator("[data-uid=\\"{uid}\\"]").click()',
    'browser_fill': 'page.locator("{selector}").fill("{value}")',
    'mcp_chrome-devtoo_fill': 'page.locator("[data-uid=\\"{uid}\\"]").fill("{value}")',
    'browser_type': 'page.locator("{selector}").type("{text}")',
    'mcp_chrome-devtoo_type': 'page.locator("[data-uid=\\"{uid}\\"]").type("{text}")',
    'browser_select': 'page.locator("{selector}").select_option("{value}")',
    'browser_hover': 'page.locator("{selector}").hover()',
    'mcp_chrome-devtoo_hover': 'page.locator("[data-uid=\\"{uid}\\"]").hover()',
    'browser_screenshot': 'page.screenshot(path="{path}")',
    'mcp_chrome-devtoo_screenshot': 'page.screenshot(path="{path}")',
    'browser_wait': 'page.wait_for_timeout({timeout})',
    'mcp_chrome-devtoo_wait_for': 'page.wait_for_selector("{selector}")',
    'browser_press': 'page.keyboard.press("{key}")',
    'mcp_chrome-devtoo_press_key': 'page.keyboard.press("{key}")',
}

# Playwright 脚本模板
SCRIPT_TEMPLATE = '''"""
自动化测试脚本
生成时间: {generated_at}
测试用例: {test_case_name}
目标URL: {target_url}
"""
import pytest
from playwright.sync_api import Page, expect


class Test{class_name}:
    """
    {test_case_name} 自动化测试
    """
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """测试前置设置"""
        self.page = page
        # 设置默认超时
        page.set_default_timeout({timeout} * 1000)
    
    def test_{method_name}(self, page: Page):
        """
        {test_description}
        """
{test_steps}
'''

# 简化模板（无 pytest，支持录屏）
SIMPLE_SCRIPT_TEMPLATE = '''"""
自动化测试脚本
生成时间: {generated_at}
测试用例: {test_case_name}
目标URL: {target_url}
"""
import os
from playwright.sync_api import sync_playwright


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless={headless})
        
        # 录屏配置
        video_dir = os.environ.get('PLAYWRIGHT_VIDEO_DIR', '')
        context_options = {{"ignore_https_errors": True}}
        if video_dir:
            context_options["record_video_dir"] = video_dir
            context_options["record_video_size"] = {{"width": 1280, "height": 720}}
        
        context = browser.new_context(**context_options)
        page = context.new_page()
        page.set_default_timeout({timeout} * 1000)
        
        try:
{test_steps}
            print("测试执行成功")
        except Exception as e:
            print(f"测试执行失败: {{e}}")
            page.screenshot(path="error_screenshot.png")
            raise
        finally:
            # 关闭上下文以确保视频保存完成
            context.close()
            browser.close()


if __name__ == "__main__":
    run()
'''


class PlaywrightScriptGenerator:
    """
    将 Agent 记录的 MCP 操作步骤转换为 Playwright Python 脚本
    """
    
    def __init__(self, use_pytest: bool = True):
        self.use_pytest = use_pytest
    
    def generate_script(
        self,
        recorded_steps: List[Dict[str, Any]],
        test_case_name: str,
        target_url: str = '',
        timeout_seconds: int = 30,
        headless: bool = True,
        description: str = ''
    ) -> str:
        """
        生成 Playwright 脚本
        
        Args:
            recorded_steps: 记录的操作步骤列表
            test_case_name: 测试用例名称
            target_url: 目标URL
            timeout_seconds: 超时时间
            headless: 是否无头模式
            description: 测试描述
        
        Returns:
            生成的 Python 脚本字符串
        """
        steps_code = self._generate_steps_code(recorded_steps)
        
        # 清理类名和方法名
        class_name = self._sanitize_name(test_case_name, capitalize=True)
        method_name = self._sanitize_name(test_case_name, capitalize=False)
        
        if self.use_pytest:
            indent = '        '  # pytest 方法内的缩进
            formatted_steps = '\n'.join(f'{indent}{line}' for line in steps_code if line.strip())
            
            return SCRIPT_TEMPLATE.format(
                generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                test_case_name=test_case_name,
                target_url=target_url or '未指定',
                class_name=class_name,
                method_name=method_name,
                timeout=timeout_seconds,
                test_description=description or test_case_name,
                test_steps=formatted_steps
            )
        else:
            indent = '            '  # 简单模板的缩进
            formatted_steps = '\n'.join(f'{indent}{line}' for line in steps_code if line.strip())
            
            return SIMPLE_SCRIPT_TEMPLATE.format(
                generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                test_case_name=test_case_name,
                target_url=target_url or '未指定',
                timeout=timeout_seconds,
                headless=str(headless),
                test_steps=formatted_steps
            )
    
    def _generate_steps_code(self, recorded_steps: List[Dict[str, Any]]) -> List[str]:
        """
        将记录的步骤转换为代码行
        """
        code_lines = []
        
        for i, step in enumerate(recorded_steps, 1):
            tool_name = step.get('tool_name', '')
            tool_input = step.get('tool_input', {})
            
            # 添加步骤注释 - 清理为单行并移除特殊字符
            step_comment = step.get('description', f'步骤 {i}')
            step_comment = self._sanitize_comment(step_comment)
            code_lines.append(f'# {step_comment}')
            
            # 生成代码
            code_line = self._generate_step_code(tool_name, tool_input)
            if code_line:
                code_lines.append(code_line)
            else:
                code_lines.append(f'# 未知操作: {tool_name}')
            
            code_lines.append('')  # 空行分隔
        
        return code_lines
    
    def _sanitize_comment(self, comment: str) -> str:
        """
        清理注释文本，确保是有效的 Python 单行注释
        - 替换换行符为空格
        - 限制长度
        - 移除不安全的字符
        """
        if not comment:
            return ''
        # 替换换行符为空格
        sanitized = comment.replace('\n', ' ').replace('\r', ' ')
        # 移除多余空格
        sanitized = ' '.join(sanitized.split())
        # 限制长度
        if len(sanitized) > 80:
            sanitized = sanitized[:77] + '...'
        return sanitized
    
    def _generate_step_code(self, tool_name: str, tool_input: Dict[str, Any]) -> Optional[str]:
        """
        根据工具名和输入生成单行代码
        """
        template = TOOL_MAPPING.get(tool_name)
        if not template:
            return None
        
        try:
            # 处理不同工具的参数
            params = self._extract_params(tool_name, tool_input)
            return template.format(**params)
        except KeyError as e:
            logger.warning(f"生成脚本时缺少参数: {e}, tool={tool_name}, input={tool_input}")
            return f'# 参数缺失: {tool_name}'
    
    def _extract_params(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        从工具输入中提取模板所需的参数
        """
        params = {}
        
        # 统一处理 URL
        if 'url' in tool_input:
            params['url'] = tool_input['url']
        
        # 处理选择器
        if 'selector' in tool_input:
            params['selector'] = self._escape_string(tool_input['selector'])
        elif 'uid' in tool_input:
            params['uid'] = tool_input['uid']
        elif 'element' in tool_input:
            params['selector'] = self._escape_string(tool_input['element'])
        
        # 处理值
        if 'value' in tool_input:
            params['value'] = self._escape_string(tool_input['value'])
        if 'text' in tool_input:
            params['text'] = self._escape_string(tool_input['text'])
        
        # 处理按键
        if 'key' in tool_input:
            params['key'] = tool_input['key']
        
        # 处理超时
        if 'timeout' in tool_input:
            params['timeout'] = tool_input['timeout']
        
        # 处理截图路径
        if 'path' in tool_input:
            params['path'] = tool_input['path']
        elif tool_name in ['browser_screenshot', 'mcp_chrome-devtoo_screenshot']:
            params['path'] = f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        
        return params
    
    def _escape_string(self, s: str) -> str:
        """
        安全转义字符串，用于嵌入 Python 代码
        使用 repr() 确保所有特殊字符都被正确转义
        """
        if not isinstance(s, str):
            s = str(s)
        # 使用 repr() 生成安全的 Python 字符串表示
        # 然后去掉外层引号，因为模板中已有引号
        escaped = repr(s)
        # repr 返回 'string' 或 "string"，去掉外层引号
        if escaped.startswith("'") and escaped.endswith("'"):
            return escaped[1:-1].replace('"', '\\"')
        elif escaped.startswith('"') and escaped.endswith('"'):
            return escaped[1:-1]
        return escaped
    
    def _sanitize_name(self, name: str, capitalize: bool = False) -> str:
        """
        清理名称，使其成为有效的 Python 标识符
        """
        import re
        
        # 移除非字母数字字符
        sanitized = re.sub(r'[^\w\s]', '', name)
        # 用下划线替换空格
        sanitized = re.sub(r'\s+', '_', sanitized)
        # 确保不以数字开头
        if sanitized and sanitized[0].isdigit():
            sanitized = '_' + sanitized
        
        if capitalize:
            # 转为 PascalCase
            return ''.join(word.capitalize() for word in sanitized.split('_'))
        else:
            # 转为 snake_case
            return sanitized.lower()


class TestCaseTemplateGenerator:
    """
    测试用例模板生成器
    基于历史用例和知识库内容生成新的测试用例
    """
    
    def __init__(self, knowledge_service=None):
        self.knowledge_service = knowledge_service
    
    async def generate_test_case_template(
        self,
        requirement: str,
        project_id: str,
        knowledge_base_id: str = None,
        similar_cases: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        基于需求和历史用例生成测试用例模板
        
        Args:
            requirement: 需求描述
            project_id: 项目ID
            knowledge_base_id: 知识库ID
            similar_cases: 相似的历史测试用例
            
        Returns:
            生成的测试用例模板
        """
        try:
            # 1. 从知识库检索相关需求文档
            context_docs = []
            if knowledge_base_id and self.knowledge_service:
                kb_service = self.knowledge_service(knowledge_base_id)
                await kb_service.initialize()
                
                search_results = await kb_service.search_knowledge(
                    f"需求 测试 {requirement}", top_k=3
                )
                context_docs = search_results
            
            # 2. 分析相似测试用例
            similar_patterns = self._analyze_similar_cases(similar_cases or [])
            
            # 3. 生成测试用例结构
            test_case_template = {
                'name': f'{requirement} - 测试用例',
                'description': f'基于需求"{requirement}"生成的测试用例',
                'priority': 'medium',
                'type': 'functional',
                'preconditions': [],
                'test_steps': [],
                'expected_results': [],
                'test_data': {},
                'tags': [],
                'estimated_time': '30分钟'
            }
            
            # 4. 基于上下文生成具体内容
            if context_docs:
                test_case_template['context_sources'] = [
                    {
                        'source': doc.get('metadata', {}).get('source', '未知'),
                        'content_preview': doc.get('content', '')[:200] + '...'
                    }
                    for doc in context_docs
                ]
            
            # 5. 基于相似用例生成步骤模板
            if similar_patterns:
                test_case_template['suggested_steps'] = similar_patterns.get('common_steps', [])
                test_case_template['suggested_tags'] = similar_patterns.get('common_tags', [])
            
            # 6. 生成基础测试步骤模板
            basic_steps = self._generate_basic_test_steps(requirement)
            test_case_template['test_steps'] = basic_steps
            
            return test_case_template
            
        except Exception as e:
            logger.error(f"生成测试用例模板失败: {e}")
            return {
                'error': str(e),
                'name': f'{requirement} - 测试用例',
                'description': '生成失败，请手动创建'
            }
    
    def _analyze_similar_cases(self, similar_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析相似测试用例，提取通用模式
        """
        if not similar_cases:
            return {}
        
        # 提取通用步骤
        all_steps = []
        all_tags = []
        
        for case in similar_cases:
            if 'test_steps' in case:
                all_steps.extend(case['test_steps'])
            if 'tags' in case:
                all_tags.extend(case['tags'])
        
        # 统计频率
        step_frequency = {}
        tag_frequency = {}
        
        for step in all_steps:
            step_key = step.get('action', '') if isinstance(step, dict) else str(step)
            step_frequency[step_key] = step_frequency.get(step_key, 0) + 1
        
        for tag in all_tags:
            tag_frequency[tag] = tag_frequency.get(tag, 0) + 1
        
        # 返回高频项
        common_steps = [
            step for step, freq in step_frequency.items() 
            if freq >= len(similar_cases) * 0.5  # 出现在50%以上的用例中
        ]
        
        common_tags = [
            tag for tag, freq in tag_frequency.items()
            if freq >= len(similar_cases) * 0.3  # 出现在30%以上的用例中
        ]
        
        return {
            'common_steps': common_steps,
            'common_tags': common_tags,
            'total_analyzed': len(similar_cases)
        }
    
    def _generate_basic_test_steps(self, requirement: str) -> List[Dict[str, Any]]:
        """
        基于需求生成基础测试步骤模板
        """
        # 根据需求关键词生成不同类型的测试步骤
        steps = []
        
        # 登录相关
        if any(keyword in requirement for keyword in ['登录', '认证', '权限']):
            steps.extend([
                {
                    'step_number': len(steps) + 1,
                    'action': '打开登录页面',
                    'expected_result': '页面正常加载，显示登录表单'
                },
                {
                    'step_number': len(steps) + 2,
                    'action': '输入有效的用户名和密码',
                    'expected_result': '输入框正常接受输入'
                },
                {
                    'step_number': len(steps) + 3,
                    'action': '点击登录按钮',
                    'expected_result': '成功登录，跳转到主页面'
                }
            ])
        
        # 表单相关
        if any(keyword in requirement for keyword in ['表单', '提交', '保存', '创建']):
            steps.extend([
                {
                    'step_number': len(steps) + 1,
                    'action': '填写必填字段',
                    'expected_result': '所有必填字段正常接受输入'
                },
                {
                    'step_number': len(steps) + 2,
                    'action': '点击提交按钮',
                    'expected_result': '表单验证通过，数据成功提交'
                }
            ])
        
        # 搜索相关
        if any(keyword in requirement for keyword in ['搜索', '查询', '筛选']):
            steps.extend([
                {
                    'step_number': len(steps) + 1,
                    'action': '在搜索框输入关键词',
                    'expected_result': '搜索框正常接受输入'
                },
                {
                    'step_number': len(steps) + 2,
                    'action': '点击搜索按钮或按回车',
                    'expected_result': '显示搜索结果列表'
                }
            ])
        
        # 如果没有匹配的关键词，生成通用步骤
        if not steps:
            steps = [
                {
                    'step_number': 1,
                    'action': '访问相关功能页面',
                    'expected_result': '页面正常加载'
                },
                {
                    'step_number': 2,
                    'action': '执行核心操作',
                    'expected_result': '操作成功完成'
                },
                {
                    'step_number': 3,
                    'action': '验证结果',
                    'expected_result': '结果符合预期'
                }
            ]
        
        return steps