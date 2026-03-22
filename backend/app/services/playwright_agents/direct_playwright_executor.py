"""
Python Playwright 执行测试（不通过 MCP）
"""
import logging
import time
import re
import asyncio
import base64
from typing import Dict, Any, List
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page

logger = logging.getLogger(__name__)


class DirectPlaywrightExecutor:
    """直接使用 Playwright 执行测试"""
    
    async def execute_test(
        self,
        code: str,
        browser: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """
        直接执行测试代码
        
        Args:
            code: 测试代码
            browser: 浏览器类型
            headless: 是否无头模式
            
        Returns:
            执行结果，包含步骤截图
        """
        try:
            logger.info("开始直接执行 Playwright 测试")
            start_time = time.time()
            
            # 解析测试代码
            steps = self._parse_test_steps(code)
            screenshots = []
            
            overall_status = "success"
            stdout_lines = []
            stderr_lines = []
            
            # 启动 Playwright
            async with async_playwright() as p:
                # 启动浏览器
                browser_type = getattr(p, browser)
                browser_instance = await browser_type.launch(headless=headless)
                page = await browser_instance.new_page(viewport={'width': 1920, 'height': 1080})
                
                stdout_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] 浏览器已启动")
                
                try:
                    # 执行每个步骤
                    for i, step in enumerate(steps, 1):
                        step_start_time = time.time()
                        
                        try:
                            logger.info(f"执行步骤 {i}/{len(steps)}: {step['description']}")
                            stdout_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] 步骤 {i}: {step['description']}")
                            
                            screenshot_before = None
                            screenshot_after = None
                            
                            # 根据操作类型执行
                            if step['action'] == 'navigate':
                                # 导航
                                await page.goto(step['url'], wait_until='networkidle', timeout=30000)
                                await asyncio.sleep(1)
                                
                                # 导航后截图
                                screenshot_bytes = await page.screenshot(type='jpeg', quality=60)
                                screenshot_after = base64.b64encode(screenshot_bytes).decode('utf-8')
                                
                            elif step['action'] == 'click':
                                # 点击前截图
                                screenshot_bytes = await page.screenshot(type='jpeg', quality=60)
                                screenshot_before = base64.b64encode(screenshot_bytes).decode('utf-8')
                                
                                # 点击
                                await page.locator(step['selector']).click(timeout=10000)
                                await asyncio.sleep(1)
                                
                                # 点击后截图
                                screenshot_bytes = await page.screenshot(type='jpeg', quality=60)
                                screenshot_after = base64.b64encode(screenshot_bytes).decode('utf-8')
                                
                            elif step['action'] == 'type':
                                # 输入前截图
                                screenshot_bytes = await page.screenshot(type='jpeg', quality=60)
                                screenshot_before = base64.b64encode(screenshot_bytes).decode('utf-8')
                                
                                # 输入
                                await page.locator(step['selector']).fill(step['text'], timeout=10000)
                                await asyncio.sleep(0.5)
                                
                                # 输入后截图
                                screenshot_bytes = await page.screenshot(type='jpeg', quality=60)
                                screenshot_after = base64.b64encode(screenshot_bytes).decode('utf-8')
                                
                            elif step['action'] == 'press':
                                # 按键前截图
                                screenshot_bytes = await page.screenshot(type='jpeg', quality=60)
                                screenshot_before = base64.b64encode(screenshot_bytes).decode('utf-8')
                                
                                # 按键
                                await page.keyboard.press(step['key'])
                                await asyncio.sleep(1)
                                
                                # 按键后截图
                                screenshot_bytes = await page.screenshot(type='jpeg', quality=60)
                                screenshot_after = base64.b64encode(screenshot_bytes).decode('utf-8')
                                
                            elif step['action'] == 'wait_load':
                                # 等待加载
                                await page.wait_for_load_state(step.get('state', 'load'), timeout=30000)
                                
                            elif step['action'] == 'wait':
                                # 等待元素
                                await page.wait_for_selector(step['selector'], timeout=30000)
                            
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
                                screenshot_bytes = await page.screenshot(type='jpeg', quality=60)
                                screenshot_after = base64.b64encode(screenshot_bytes).decode('utf-8')
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
                
                finally:
                    # 关闭浏览器
                    await browser_instance.close()
                    stdout_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] 浏览器已关闭")
            
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
            logger.error(f"Playwright 执行失败: {e}", exc_info=True)
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
    
    def _parse_test_steps(self, code: str) -> List[Dict[str, Any]]:
        """解析测试代码，提取步骤"""
        steps = []
        lines = code.split('\n')
        variable_selectors = {}
        
        for line in lines:
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith('#') or line.startswith('//') or line.startswith('"""') or line.startswith("'''"):
                continue
            
            # 记录变量赋值
            if '= page.locator(' in line or '=page.locator(' in line:
                var_match = re.search(r'(\w+)\s*=\s*(?:await\s+)?page\.locator\(["\']([^"\']+)["\']\)', line)
                if var_match:
                    var_name = var_match.group(1)
                    selector = var_match.group(2)
                    variable_selectors[var_name] = selector
                    continue
            
            # 导航
            if '.goto(' in line:
                url_match = re.search(r'["\']([^"\']+)["\']', line)
                if url_match:
                    steps.append({
                        "action": "navigate",
                        "url": url_match.group(1),
                        "description": f"打开页面 {url_match.group(1)}"
                    })
            
            # 输入
            elif '.fill(' in line:
                var_match = re.search(r'(\w+)\.fill\(', line)
                if var_match:
                    var_name = var_match.group(1)
                    selector = variable_selectors.get(var_name, var_name)
                    text_match = re.search(r'\.fill\(["\']([^"\']*)["\']\)', line)
                    text = text_match.group(1) if text_match else ""
                    
                    desc = f"在搜索框中输入 '{text}'" if text else "清空搜索框"
                    if selector != "#kw" and "search" not in var_name.lower():
                        desc = f"在输入框中输入 '{text}'" if text else "清空输入框"
                    
                    steps.append({
                        "action": "type",
                        "selector": selector,
                        "text": text,
                        "description": desc
                    })
            
            # 点击
            elif '.click()' in line:
                var_match = re.search(r'(\w+)\.click\(\)', line)
                if var_match:
                    var_name = var_match.group(1)
                    selector = variable_selectors.get(var_name, var_name)
                    
                    desc = "点击搜索按钮" if selector == "#su" or "button" in var_name.lower() else "点击按钮"
                    
                    steps.append({
                        "action": "click",
                        "selector": selector,
                        "description": desc
                    })
            
            # 按键
            elif '.press(' in line:
                key_match = re.search(r'["\']([^"\']+)["\']', line)
                if key_match:
                    key = key_match.group(1)
                    key_desc = {"Enter": "回车", "Escape": "ESC", "Tab": "Tab"}.get(key, key)
                    steps.append({
                        "action": "press",
                        "key": key,
                        "description": f"按下 {key_desc} 键"
                    })
            
            # 等待
            elif 'wait_for_load_state(' in line or 'waitForLoadState(' in line:
                state_match = re.search(r'["\']([^"\']+)["\']', line)
                state = state_match.group(1) if state_match else "load"
                state_desc = {"networkidle": "网络空闲", "load": "页面加载"}.get(state, state)
                steps.append({
                    "action": "wait_load",
                    "state": state,
                    "description": f"等待{state_desc}完成"
                })
            
            elif 'wait_for_selector(' in line or 'waitForSelector(' in line:
                selector_match = re.search(r'["\']([^"\']+)["\']', line)
                if selector_match:
                    steps.append({
                        "action": "wait",
                        "selector": selector_match.group(1),
                        "description": "等待元素出现"
                    })
        
        if not steps:
            steps.append({"action": "execute", "description": "执行测试代码"})
        
        logger.info(f"解析到 {len(steps)} 个步骤")
        return steps
