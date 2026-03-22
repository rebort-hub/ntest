"""
Healer Agent - 修复器
"""
import logging
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

logger = logging.getLogger(__name__)


class HealerAgent:
    """自愈修复器Agent - 直接使用 Playwright"""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    async def _init_browser(self):
        """初始化浏览器（支持多版本降级）"""
        if self.browser is None:
            self.playwright = await async_playwright().start()
            
            # 尝试不同的浏览器配置
            browser_configs = [
                # 尝试使用系统已安装的旧版本
                {
                    'channel': None,
                    'executable_path': None,
                    'headless': True
                },
                # 尝试使用 Chrome/Edge
                {
                    'channel': 'chrome',
                    'executable_path': None,
                    'headless': True
                },
                {
                    'channel': 'msedge',
                    'executable_path': None,
                    'headless': True
                },
            ]
            
            last_error = None
            for config in browser_configs:
                try:
                    logger.info(f"尝试启动浏览器: {config}")
                    
                    launch_options = {
                        'headless': config['headless'],
                        'args': ['--no-sandbox', '--disable-setuid-sandbox']
                    }
                    
                    if config['channel']:
                        launch_options['channel'] = config['channel']
                    
                    if config['executable_path']:
                        launch_options['executable_path'] = config['executable_path']
                    
                    self.browser = await self.playwright.chromium.launch(**launch_options)
                    logger.info(f"✓ 浏览器启动成功")
                    break
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"浏览器启动失败: {str(e)[:100]}")
                    continue
            
            if self.browser is None:
                await self.playwright.stop()
                self.playwright = None
                raise Exception(
                    f"无法启动浏览器。请运行以下命令安装 Playwright 浏览器：\n"
                    f"cd backend\n"
                    f".venv\\Scripts\\playwright.exe install chromium\n\n"
                    f"或者确保系统已安装 Chrome/Edge 浏览器。\n"
                    f"最后一次错误: {str(last_error)}"
                )
            
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            self.page = await self.context.new_page()
    
    async def _close_browser(self):
        """关闭浏览器"""
        if self.page:
            await self.page.close()
            self.page = None
        if self.context:
            await self.context.close()
            self.context = None
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
    
    async def heal_failed_test(
        self,
        execution_data: Dict[str, Any],
        original_code: str,
        language: str = "typescript"
    ) -> Dict[str, Any]:
        """
        修复失败的测试
        结合真实页面分析和错误日志，提供更准确的修复
        
        Args:
            execution_data: 执行数据（包含错误信息）
            original_code: 原始测试代码
            language: 编程语言
            
        Returns:
            修复结果
        """
        try:
            logger.info(f"开始分析并修复失败的测试")
            
            # 1. 分析错误
            error_analysis = await self._analyze_error_with_context(
                execution_data,
                original_code,
                language
            )
            
            # 2. 获取当前页面状态（如果可能）
            current_page_state = await self._get_current_page_state(
                execution_data.get('url', '')
            )
            
            # 3. 生成修复代码
            fixed_code = await self._generate_fixed_code_with_context(
                original_code,
                error_analysis,
                current_page_state,
                language
            )
            
            # 4. 提取变更说明
            changes = self._extract_detailed_changes(original_code, fixed_code)
            
            result = {
                "error_analysis": error_analysis,
                "fixed_code": fixed_code,
                "changes": changes,
                "fix_description": self._generate_fix_description(changes),
                "page_state": current_page_state,
                "confidence": self._calculate_fix_confidence(changes, current_page_state)
            }
            
            logger.info("✓ 测试修复完成")
            return result
            
        except Exception as e:
            logger.error(f"测试修复失败: {str(e)}")
            raise
        finally:
            # 确保关闭浏览器
            try:
                await self._close_browser()
            except:
                pass
    
    async def _get_current_page_state(self, url: str) -> Optional[Dict[str, Any]]:
        """获取当前页面状态用于修复分析"""
        if not url:
            return None
        
        try:
            await self._init_browser()
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 获取页面快照
            snapshot = {
                "title": await self.page.title(),
                "url": self.page.url,
                "available_selectors": await self._get_available_selectors()
            }
            
            return snapshot
            
        except Exception as e:
            logger.warning(f"无法获取页面状态: {str(e)}")
            return None
    
    async def _get_available_selectors(self) -> Dict[str, List[str]]:
        """获取页面上可用的选择器"""
        try:
            selectors = {
                "buttons": await self.page.evaluate('''
                    () => {
                        const buttons = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]'));
                        return buttons.slice(0, 20).map(btn => ({
                            text: btn.innerText || btn.value || '',
                            id: btn.id || '',
                            class: btn.className || ''
                        })).filter(btn => btn.text);
                    }
                '''),
                "links": await self.page.evaluate('''
                    () => {
                        const links = Array.from(document.querySelectorAll('a'));
                        return links.slice(0, 20).map(a => ({
                            text: a.innerText.trim(),
                            href: a.href,
                            id: a.id || ''
                        })).filter(link => link.text);
                    }
                '''),
                "inputs": await self.page.evaluate('''
                    () => {
                        const inputs = Array.from(document.querySelectorAll('input, textarea'));
                        return inputs.slice(0, 20).map(input => ({
                            type: input.type || 'text',
                            name: input.name || '',
                            id: input.id || '',
                            placeholder: input.placeholder || ''
                        }));
                    }
                ''')
            }
            return selectors
        except Exception as e:
            logger.warning(f"获取选择器失败: {str(e)}")
            return {}
    
    async def _analyze_error_with_context(
        self,
        execution_data: Dict[str, Any],
        original_code: str,
        language: str
    ) -> str:
        """分析错误原因（带上下文）"""
        
        error_message = execution_data.get('error_message', '')
        stderr = execution_data.get('stderr', '')
        
        prompt = f"""
你是一个专业的测试工程师，需要分析以下Playwright测试失败的原因。

测试代码 ({language}):
```
{original_code}
```

错误信息:
{error_message}

错误输出:
{stderr}

请详细分析：
1. 失败的根本原因是什么？
2. 可能是哪些因素导致的？
   - 选择器问题（元素不存在、选择器不准确）
   - 时序问题（元素未加载、动画未完成）
   - 网络问题（请求超时、资源加载失败）
   - 断言问题（预期值不正确）
   - 其他问题
3. 推荐的修复方案是什么？
4. 修复的优先级和置信度如何？

请用结构化的方式描述分析结果。
"""
        
        analysis = await self.llm_service.generate_text(
            prompt=prompt,
            temperature=0.3,
            max_tokens=1500
        )
        
        return analysis
    
    async def _generate_fixed_code_with_context(
        self,
        original_code: str,
        error_analysis: str,
        page_state: Optional[Dict[str, Any]],
        language: str
    ) -> str:
        """生成修复后的代码（带页面状态上下文）"""
        
        # 构建页面状态信息
        page_info = ""
        if page_state and page_state.get('available_selectors'):
            selectors = page_state['available_selectors']
            page_info = f"""

## 当前页面可用元素：

按钮:
{self._format_selectors(selectors.get('buttons', []))}

链接:
{self._format_selectors(selectors.get('links', []))}

输入框:
{self._format_selectors(selectors.get('inputs', []))}
"""
        
        prompt = f"""
你是一个专业的测试工程师，需要修复以下失败的Playwright测试代码。

原始代码 ({language}):
```
{original_code}
```

错误分析:
{error_analysis}
{page_info}

请生成修复后的代码，要求：
1. 保持原有测试逻辑不变
2. 根据错误分析修复导致失败的问题
3. 如果是选择器问题，使用页面上实际存在的元素
4. 添加必要的等待逻辑（waitForSelector, waitForLoadState等）
5. 添加适当的错误处理和重试机制
6. 使用更可靠的现代选择器（getByRole, getByText等）
7. 添加注释说明修复的内容
8. 代码应该是可直接运行的

只返回修复后的完整代码，不要添加额外说明。

```{language}
"""
        
        response = await self.llm_service.generate_text(
            prompt=prompt,
            temperature=0.2,  # 更低温度确保修复质量
            max_tokens=4000
        )
        
        # 提取代码块
        import re
        code_pattern = r'```(?:typescript|python|javascript)?\n?([\s\S]*?)```'
        matches = re.findall(code_pattern, response)
        
        if matches:
            return matches[0].strip()
        
        # 如果没有代码块，返回整个响应
        return response.strip()
    
    def _format_selectors(self, selectors: List[Dict[str, str]]) -> str:
        """格式化选择器信息"""
        if not selectors:
            return "  (无)"
        
        formatted = []
        for sel in selectors[:10]:  # 限制数量
            parts = []
            if sel.get('text'):
                parts.append(f"text=\"{sel['text']}\"")
            if sel.get('id'):
                parts.append(f"id=\"{sel['id']}\"")
            if sel.get('name'):
                parts.append(f"name=\"{sel['name']}\"")
            if sel.get('type'):
                parts.append(f"type=\"{sel['type']}\"")
            
            if parts:
                formatted.append(f"  - {', '.join(parts)}")
        
        return '\n'.join(formatted) if formatted else "  (无)"
    
    def _extract_detailed_changes(self, original_code: str, fixed_code: str) -> List[Dict[str, Any]]:
        """提取详细的代码变更"""
        import difflib
        
        original_lines = original_code.splitlines()
        fixed_lines = fixed_code.splitlines()
        
        diff = list(difflib.unified_diff(
            original_lines,
            fixed_lines,
            lineterm='',
            n=3
        ))
        
        changes = []
        
        if diff:
            change = {
                "type": "code_modification",
                "description": "修改了测试代码以修复失败问题",
                "diff": '\n'.join(diff),
                "lines_added": len([l for l in diff if l.startswith('+') and not l.startswith('+++')]),
                "lines_removed": len([l for l in diff if l.startswith('-') and not l.startswith('---')])
            }
            changes.append(change)
        
        # 分析具体变更类型
        new_lines = [line for line in fixed_lines if line not in original_lines]
        
        # 检查等待逻辑
        wait_keywords = ['wait', 'waitFor', 'waitUntil', 'sleep', 'delay']
        if any(keyword in line.lower() for line in new_lines for keyword in wait_keywords):
            changes.append({
                "type": "wait_added",
                "description": "添加了等待逻辑以处理时序问题",
                "impact": "high"
            })
        
        # 检查错误处理
        error_keywords = ['try', 'catch', 'except', 'finally', 'rescue']
        if any(keyword in line for line in new_lines for keyword in error_keywords):
            changes.append({
                "type": "error_handling_added",
                "description": "添加了错误处理逻辑",
                "impact": "medium"
            })
        
        # 检查选择器变更
        original_selectors = set(self._extract_selectors(original_code))
        fixed_selectors = set(self._extract_selectors(fixed_code))
        
        if original_selectors != fixed_selectors:
            added = fixed_selectors - original_selectors
            removed = original_selectors - fixed_selectors
            changes.append({
                "type": "selector_updated",
                "description": "更新了元素选择器以提高可靠性",
                "added_selectors": list(added),
                "removed_selectors": list(removed),
                "impact": "high"
            })
        
        # 检查断言变更
        assertion_keywords = ['expect', 'assert', 'should', 'toBe', 'toEqual']
        if any(keyword in line for line in new_lines for keyword in assertion_keywords):
            changes.append({
                "type": "assertion_updated",
                "description": "更新了断言逻辑",
                "impact": "medium"
            })
        
        # 检查重试逻辑
        retry_keywords = ['retry', 'attempt', 'repeat']
        if any(keyword in line.lower() for line in new_lines for keyword in retry_keywords):
            changes.append({
                "type": "retry_added",
                "description": "添加了重试机制以提高稳定性",
                "impact": "medium"
            })
        
        return changes
    
    def _extract_selectors(self, code: str) -> List[str]:
        """提取代码中的选择器"""
        import re
        
        # 匹配常见的选择器模式
        patterns = [
            r'getByRole\([\'"]([^\'"]+)[\'"]',
            r'getByText\([\'"]([^\'"]+)[\'"]',
            r'getByLabel\([\'"]([^\'"]+)[\'"]',
            r'locator\([\'"]([^\'"]+)[\'"]',
            r'querySelector\([\'"]([^\'"]+)[\'"]',
        ]
        
        selectors = []
        for pattern in patterns:
            matches = re.findall(pattern, code)
            selectors.extend(matches)
        
        return selectors
    
    def _calculate_fix_confidence(
        self,
        changes: List[Dict[str, Any]],
        page_state: Optional[Dict[str, Any]]
    ) -> float:
        """计算修复置信度"""
        confidence = 0.5  # 基础置信度
        
        # 如果有页面状态信息，增加置信度
        if page_state and page_state.get('available_selectors'):
            confidence += 0.2
        
        # 根据变更类型调整置信度
        for change in changes:
            change_type = change.get('type', '')
            impact = change.get('impact', 'low')
            
            if change_type == 'selector_updated' and impact == 'high':
                confidence += 0.15
            elif change_type == 'wait_added' and impact == 'high':
                confidence += 0.1
            elif change_type == 'error_handling_added':
                confidence += 0.05
        
        # 限制在 0-1 范围内
        return min(1.0, max(0.0, confidence))
    
    def _generate_fix_description(self, changes: List[Dict[str, Any]]) -> str:
        """生成修复说明"""
        if not changes:
            return "未检测到明显变更"
        
        descriptions = []
        high_impact_changes = []
        
        for change in changes:
            desc = change.get('description', '')
            impact = change.get('impact', 'low')
            
            if desc:
                if impact == 'high':
                    high_impact_changes.append(desc)
                else:
                    descriptions.append(desc)
        
        # 高影响变更放在前面
        all_descriptions = high_impact_changes + descriptions
        
        if not all_descriptions:
            return "代码已修复"
        
        # 生成简洁的描述
        if len(all_descriptions) == 1:
            return all_descriptions[0]
        elif len(all_descriptions) <= 3:
            return '; '.join(all_descriptions)
        else:
            return f"{'; '.join(all_descriptions[:2])}; 以及其他{len(all_descriptions)-2}项优化"
