"""
基于 MCP 的 Playwright 执行器
"""
import logging
import time
import json
import asyncio
import re
from typing import Dict, Any, List
from datetime import datetime
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger(__name__)


class MCPExecutorAgent:
    """基于 MCP 的 Playwright 执行器代理"""
    
    def __init__(self):
        self.mcp_client = None
    
    async def execute_with_mcp(
        self,
        code: str,
        mcp_config: Dict[str, Any],
        browser: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """
        使用 MCP 执行测试代码并记录每个步骤的截图
        
        使用官方 Playwright MCP Server 执行浏览器操作，确保稳定性和完整性
        
        Args:
            code: 测试代码
            mcp_config: MCP 配置
            browser: 浏览器类型
            headless: 是否无头模式
            
        Returns:
            执行结果，包含步骤截图
        """
        try:
            logger.info("开始使用 Playwright MCP 执行测试代码")
            start_time = time.time()
            
            # 解析测试代码，提取步骤
            steps = self._parse_test_steps(code)
            screenshots = []
            
            # 创建 MCP 客户端配置（使用 N-Tester MCP，与探索功能完全相同）
            mcp_url = mcp_config.get('url', 'http://127.0.0.1:8006')
            
            client_config = {
                "n-tester": {
                    "url": mcp_url,
                    "transport": "streamable-http"
                }
            }
            
            logger.info(f"MCP 配置: {client_config}")
            
            self.mcp_client = MultiServerMCPClient(client_config)
            
            overall_status = "success"
            stdout_lines = []
            stderr_lines = []
            
            try:
                # 使用 N-Tester MCP（与探索功能相同）
                async with self.mcp_client.session("n-tester") as session:
                    logger.info(f"✅ N-Tester MCP Session 已建立")
                    logger.info(f"🎭 将使用增强工具调用官方 Playwright MCP")
                    stdout_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] 连接到 N-Tester MCP")
                    stdout_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] 使用增强工具（官方 Playwright MCP）")
                    
                    # 执行每个步骤
                    for i, step in enumerate(steps, 1):
                        step_start_time = time.time()
                        
                        try:
                            logger.info(f"执行步骤 {i}/{len(steps)}: {step['action']}")
                            stdout_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] 步骤 {i}: {step['description']}")
                            
                            # 操作前截图
                            screenshot_before = None
                            try:
                                if i > 1:  # 第一个步骤（通常是导航）不需要操作前截图
                                    screenshot_result = await session.call_tool("browser_screenshot_base64", {
                                        "full_page": False,
                                        "quality": 60
                                    })
                                    screenshot_before = self._extract_screenshot_from_result(screenshot_result)
                                    logger.info(f"操作前截图长度: {len(screenshot_before) if screenshot_before else 0}")
                            except Exception as e:
                                logger.warning(f"操作前截图失败: {e}")
                            
                            # 执行具体操作
                            result = None
                            screenshot_after = None
                            
                            if step['action'] == 'navigate':
                                # 导航操作 - 使用增强工具
                                result = await session.call_tool("enhanced_navigate", {
                                    "url": step['url'],
                                    "wait_until": "load"
                                })
                                
                                # 导航后截图
                                try:
                                    screenshot_result = await session.call_tool("enhanced_screenshot", {
                                        "full_page": False
                                    })
                                    screenshot_after = self._extract_screenshot_from_result(screenshot_result)
                                    logger.info(f"导航后截图完成，截图长度: {len(screenshot_after) if screenshot_after else 0}")
                                except Exception as e:
                                    logger.warning(f"导航后截图失败: {e}")
                                
                            elif step['action'] == 'click':
                                # 点击操作 - 使用增强工具
                                result = await session.call_tool("enhanced_click", {
                                    "selector": step['selector'],
                                    "timeout": 30000
                                })
                                await asyncio.sleep(1)
                                
                                # 点击后截图
                                try:
                                    screenshot_result = await session.call_tool("enhanced_screenshot", {
                                        "full_page": False
                                    })
                                    screenshot_after = self._extract_screenshot_from_result(screenshot_result)
                                except Exception as e:
                                    logger.warning(f"点击后截图失败: {e}")
                                
                            elif step['action'] == 'type':
                                # 输入操作 - 使用增强工具
                                result = await session.call_tool("enhanced_fill", {
                                    "selector": step['selector'],
                                    "value": step['text']
                                })
                                await asyncio.sleep(0.5)
                                
                                # 输入后截图
                                try:
                                    screenshot_result = await session.call_tool("enhanced_screenshot", {
                                        "full_page": False
                                    })
                                    screenshot_after = self._extract_screenshot_from_result(screenshot_result)
                                except Exception as e:
                                    logger.warning(f"输入后截图失败: {e}")
                            
                            elif step['action'] == 'press':
                                # 按键操作（如回车）
                                # 按键前截图
                                try:
                                    screenshot_result = await session.call_tool("browser_screenshot_base64", {
                                        "full_page": False,
                                        "quality": 60
                                    })
                                    screenshot_before = self._extract_screenshot_from_result(screenshot_result)
                                except Exception as e:
                                    logger.warning(f"按键前截图失败: {e}")
                                
                                # 执行按键（通过 evaluate）
                                key = step.get('key', 'Enter')
                                result = await session.call_tool("browser_evaluate", {
                                    "script": f"document.activeElement.dispatchEvent(new KeyboardEvent('keydown', {{key: '{key}'}}))"
                                })
                                await asyncio.sleep(1)
                                
                                # 按键后截图
                                try:
                                    screenshot_result = await session.call_tool("browser_screenshot_base64", {
                                        "full_page": False,
                                        "quality": 60
                                    })
                                    screenshot_after = self._extract_screenshot_from_result(screenshot_result)
                                except Exception as e:
                                    logger.warning(f"按键后截图失败: {e}")
                                
                            elif step['action'] == 'wait':
                                result = await session.call_tool("browser_wait", {
                                    "selector": step['selector']
                                })
                            
                            elif step['action'] == 'wait_load':
                                # 等待页面加载，不需要特殊处理
                                await asyncio.sleep(1)
                                result = {"status": "success"}
                            
                            # 记录步骤数据
                            step_duration = time.time() - step_start_time
                            step_data = {
                                "step_number": i,
                                "action": step['action'],
                                "description": step['description'],
                                "screenshot_before": screenshot_before,
                                "screenshot_after": screenshot_after,
                                "status": "success",
                                "duration": step_duration,
                                "timestamp": datetime.now().isoformat()
                            }
                            screenshots.append(step_data)
                            
                            stdout_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ 步骤 {i} 完成 (耗时: {step_duration:.2f}s)")
                            logger.info(f"步骤 {i} 执行成功")
                            
                        except Exception as e:
                            overall_status = "failed"
                            error_msg = str(e)
                            stderr_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ 步骤 {i} 失败: {error_msg}")
                            logger.error(f"步骤 {i} 执行失败: {e}")
                            
                            # 记录失败步骤
                            try:
                                screenshot_result = await session.call_tool("browser_screenshot_base64", {
                                    "full_page": False,
                                    "quality": 60
                                })
                                screenshot_after = self._extract_screenshot_from_result(screenshot_result)
                                screenshots.append({
                                    "step_number": i,
                                    "action": step['action'],
                                    "description": step['description'],
                                    "screenshot_after": screenshot_after,
                                    "status": "failed",
                                    "error_message": error_msg,
                                    "timestamp": datetime.now().isoformat()
                                })
                            except:
                                pass
                            
                            break
                    
                    # 关闭浏览器
                    try:
                        await session.call_tool("browser_close", {})
                        stdout_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] 浏览器已关闭")
                    except Exception as e:
                        logger.warning(f"关闭浏览器失败: {e}")
            
            except Exception as e:
                overall_status = "failed"
                stderr_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] 执行异常: {str(e)}")
                logger.error(f"MCP 执行异常: {e}", exc_info=True)
            
            duration = time.time() - start_time
            
            return {
                "status": overall_status,
                "duration": duration,
                "stdout": "\n".join(stdout_lines),
                "stderr": "\n".join(stderr_lines) if stderr_lines else None,
                "exit_code": 0 if overall_status == "success" else 1,
                "error_message": "\n".join(stderr_lines) if stderr_lines else None,
                "screenshots": screenshots,
                "videos": []
            }
            
        except Exception as e:
            logger.error(f" MCP 执行失败: {e}", exc_info=True)
            return {
                "status": "failed",
                "duration": 0,
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
                "error_message": str(e),
                "screenshots": [],
                "videos": []
            }
    
    def _extract_screenshot_from_snapshot(self, result: Any) -> str:
        """从 MCP 快照结果中提取截图"""
        try:
            if isinstance(result, dict):
                screenshot = result.get('screenshot', '')
                if screenshot:
                    logger.info(f"从字典中提取到截图，长度: {len(screenshot)}")
                return screenshot
            
            elif hasattr(result, 'content'):
                content = result.content
                if isinstance(content, list) and len(content) > 0:
                    text_content = content[0].text if hasattr(content[0], 'text') else content[0]
                    if isinstance(text_content, str):
                        try:
                            data = json.loads(text_content)
                            screenshot = data.get('screenshot', '')
                            if screenshot:
                                logger.info(f"从 JSON 内容中提取到截图，长度: {len(screenshot)}")
                            return screenshot
                        except:
                            if len(text_content) > 100:
                                logger.info(f"直接使用文本内容作为截图，长度: {len(text_content)}")
                                return text_content
            
            logger.warning(f"无法从结果中提取截图，结果类型: {type(result)}")
            return ''
        except Exception as e:
            logger.error(f"提取截图失败: {e}", exc_info=True)
            return ''
    
    def _extract_url_from_result(self, result: Any) -> str:
        """从 MCP evaluate 结果中提取 URL"""
        try:
            if isinstance(result, dict):
                return result.get('result', '')
            elif hasattr(result, 'content'):
                content = result.content
                if isinstance(content, list) and len(content) > 0:
                    text_content = content[0].text if hasattr(content[0], 'text') else content[0]
                    if isinstance(text_content, str):
                        try:
                            data = json.loads(text_content)
                            return data.get('result', '')
                        except:
                            return text_content
            return ''
        except Exception as e:
            logger.warning(f"提取 URL 失败: {e}")
            return ''
    
    def _extract_screenshot_from_snapshot(self, result: Any) -> str:
        """从 MCP browser_navigate_and_snapshot 结果中提取截图"""
        try:
            if isinstance(result, dict):
                screenshot = result.get('screenshot', '')
                if screenshot:
                    logger.info(f"从字典中提取到截图，长度: {len(screenshot)}")
                return screenshot
            
            elif hasattr(result, 'content'):
                content = result.content
                if isinstance(content, list) and len(content) > 0:
                    text_content = content[0].text if hasattr(content[0], 'text') else content[0]
                    if isinstance(text_content, str):
                        try:
                            data = json.loads(text_content)
                            screenshot = data.get('screenshot', '')
                            if screenshot:
                                logger.info(f"从 JSON 内容中提取到截图，长度: {len(screenshot)}")
                                # 验证是否是有效的 PNG/JPEG
                                if screenshot.startswith('iVBORw0KGgo') or screenshot.startswith('/9j/'):
                                    logger.info(f"截图格式有效")
                                else:
                                    logger.warning(f"截图格式可能无效，前20字符: {screenshot[:20]}")
                            return screenshot
                        except Exception as e:
                            logger.error(f"解析 JSON 失败: {e}")
                            # 如果不是 JSON，可能直接就是 base64 字符串
                            if len(text_content) > 100:
                                logger.info(f"直接使用文本内容作为截图，长度: {len(text_content)}")
                                return text_content
            
            logger.warning(f"无法从结果中提取截图，结果类型: {type(result)}")
            return ''
        except Exception as e:
            logger.error(f"提取截图失败: {e}", exc_info=True)
            return ''
    
    def _extract_screenshot_from_result(self, result: Any) -> str:
        """从 browser_screenshot_base64 结果中提取截图"""
        try:
            if isinstance(result, dict):
                screenshot = result.get('screenshot', '')
                logger.info(f"从字典提取截图: 长度={len(screenshot)}, 前50字符={screenshot[:50] if screenshot else 'N/A'}")
                return screenshot
            elif hasattr(result, 'content'):
                content = result.content
                if isinstance(content, list) and len(content) > 0:
                    text_content = content[0].text if hasattr(content[0], 'text') else content[0]
                    if isinstance(text_content, str):
                        try:
                            data = json.loads(text_content)
                            screenshot = data.get('screenshot', '')
                            logger.info(f"从 JSON 提取截图: 长度={len(screenshot)}, 前50字符={screenshot[:50] if screenshot else 'N/A'}")
                            logger.info(f"截图元数据: url={data.get('url')}, quality={data.get('quality')}, size={data.get('size')}")
                            
                            # 验证 base64 数据
                            if screenshot and len(screenshot) > 100:
                                # 检查是否全是相同字符（无效数据）
                                if screenshot[:100] == 'A' * 100:
                                    logger.error("截图数据无效：全是 'A' 字符")
                                    return ''
                                logger.info(f"截图数据看起来有效")
                            
                            return screenshot
                        except Exception as e:
                            logger.error(f"解析 JSON 失败: {e}")
                            return ''
            
            logger.warning(f"无法从结果中提取截图，结果类型: {type(result)}")
            return ''
        except Exception as e:
            logger.error(f"提取截图失败: {e}", exc_info=True)
            return ''
    
    def _parse_test_steps(self, code: str) -> List[Dict[str, Any]]:
        """解析测试代码，提取步骤（支持 Python 和 TypeScript/JavaScript）"""
        steps = []
        
        lines = code.split('\n')
        
        # 用于跟踪变量名和选择器的映射
        variable_selectors = {}
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith('#') or line.startswith('//') or line.startswith('"""') or line.startswith("'''") or line.startswith('/*'):
                continue
            
            # 记录变量赋值
            # Python: search_input = page.locator("#kw")
            # TypeScript: const searchInput = page.locator('#kw')
            if '= page.locator(' in line or '=page.locator(' in line:
                var_match = re.search(r'(\w+)\s*=\s*(?:await\s+)?page\.locator\(["\']([^"\']+)["\']\)', line)
                if var_match:
                    var_name = var_match.group(1)
                    selector = var_match.group(2)
                    variable_selectors[var_name] = selector
                    logger.debug(f"记录变量: {var_name} = {selector}")
                    continue
            
            # 1. 导航
            # Python: page.goto('url')
            # TypeScript: await page.goto('url')
            if '.goto(' in line:
                url = self._extract_string_from_line(line)
                if url:
                    steps.append({
                        "action": "navigate",
                        "url": url,
                        "description": f"打开页面 {url}"
                    })
            
            # 2. 输入
            # Python: element.fill("text")
            # TypeScript: await element.fill('text')
            elif '.fill(' in line:
                # 提取变量名
                var_match = re.search(r'(\w+)\.fill\(', line)
                if var_match:
                    var_name = var_match.group(1)
                    selector = variable_selectors.get(var_name, var_name)
                    
                    # 提取输入的文本
                    text_match = re.search(r'\.fill\(["\']([^"\']*)["\']\)', line)
                    text = text_match.group(1) if text_match else ""
                    
                    # 生成友好的描述
                    if selector == "#kw" or "search" in var_name.lower() or "input" in var_name.lower():
                        desc = f"在搜索框中输入 '{text}'" if text else "清空搜索框"
                    else:
                        desc = f"在输入框中输入 '{text}'" if text else f"清空输入框"
                    
                    steps.append({
                        "action": "type",
                        "selector": selector,
                        "text": text,
                        "description": desc
                    })
            
            # TypeScript: await element.type('text')
            elif '.type(' in line and 'page.type(' not in line:
                var_match = re.search(r'(\w+)\.type\(', line)
                if var_match:
                    var_name = var_match.group(1)
                    selector = variable_selectors.get(var_name, var_name)
                    
                    text_match = re.search(r'\.type\(["\']([^"\']*)["\']\)', line)
                    text = text_match.group(1) if text_match else ""
                    
                    desc = f"在输入框中输入 '{text}'" if text else "清空输入框"
                    
                    steps.append({
                        "action": "type",
                        "selector": selector,
                        "text": text,
                        "description": desc
                    })
            
            # 3. 点击
            # Python: element.click()
            # TypeScript: await element.click()
            elif '.click()' in line:
                # 提取变量名
                var_match = re.search(r'(\w+)\.click\(\)', line)
                if var_match:
                    var_name = var_match.group(1)
                    selector = variable_selectors.get(var_name, var_name)
                    
                    # 生成友好的描述
                    if selector == "#su" or "button" in var_name.lower() or "btn" in var_name.lower():
                        desc = "点击搜索按钮"
                    elif "link" in var_name.lower():
                        desc = f"点击链接"
                    else:
                        desc = f"点击按钮"
                    
                    steps.append({
                        "action": "click",
                        "selector": selector,
                        "description": desc
                    })
            
            # 4. 按键
            # Python: element.press("Enter")
            # TypeScript: await element.press('Enter')
            elif '.press(' in line:
                key = self._extract_string_from_line(line)
                if key:
                    key_desc = {
                        "Enter": "回车",
                        "Escape": "ESC",
                        "Tab": "Tab",
                        "Backspace": "退格"
                    }.get(key, key)
                    
                    steps.append({
                        "action": "press",
                        "key": key,
                        "description": f"按下 {key_desc} 键"
                    })
            
            # 5. 等待
            # Python: page.wait_for_load_state("networkidle")
            # TypeScript: await page.waitForLoadState('networkidle')
            elif 'wait_for_load_state(' in line or 'waitForLoadState(' in line:
                state = self._extract_string_from_line(line)
                state_desc = {
                    "networkidle": "网络空闲",
                    "load": "页面加载",
                    "domcontentloaded": "DOM加载"
                }.get(state, state) if state else "页面加载"
                
                steps.append({
                    "action": "wait_load",
                    "state": state or "load",
                    "description": f"等待{state_desc}完成"
                })
            
            elif 'wait_for_selector(' in line or 'waitForSelector(' in line:
                selector = self._extract_string_from_line(line)
                if selector:
                    steps.append({
                        "action": "wait",
                        "selector": selector,
                        "description": f"等待元素出现"
                    })
        
        if not steps:
            steps.append({
                "action": "execute",
                "description": "执行测试代码"
            })
        
        logger.info(f"解析到 {len(steps)} 个步骤:")
        for i, step in enumerate(steps, 1):
            logger.info(f"  步骤 {i}: {step['action']} - {step['description']}")
        
        return steps
    
    def _extract_string_from_line(self, line: str) -> str:
        """从代码行中提取字符串"""
        import re
        # 匹配单引号或双引号中的内容
        match = re.search(r'["\']([^"\']+)["\']', line)
        return match.group(1) if match else None
    
    def _extract_multiple_strings_from_line(self, line: str) -> List[str]:
        """从代码行中提取多个字符串（用于 fill 等需要选择器和文本的操作）"""
        import re
        matches = re.findall(r'["\']([^"\']+)["\']', line)
        return matches
    
    def _extract_selector_and_text(self, line: str) -> tuple:
        """从 fill 语句中提取选择器和文本"""
        import re
        
        # 先找到 locator 中的选择器
        locator_match = re.search(r'\.locator\(["\']([^"\']+)["\']\)', line)
        selector = locator_match.group(1) if locator_match else None
        
        # 再找到 fill 中的文本
        fill_match = re.search(r'\.fill\(["\']([^"\']*)["\']\)', line)
        text = fill_match.group(1) if fill_match else ""
        
        # 如果没有找到 locator，尝试从变量名推断
        if not selector:
            # 例如: search_input.fill("text")
            var_match = re.search(r'(\w+)\.fill\(', line)
            if var_match:
                selector = f"变量 {var_match.group(1)}"
        
        return selector, text
