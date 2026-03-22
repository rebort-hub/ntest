"""
Planner Agent
"""
import logging
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger(__name__)


class PlannerAgent:
    """测试规划器Agent - 支持 MCP 和本地 Playwright"""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.mcp_client = None
    
    async def _init_browser(self):
        """初始化浏览器（支持多版本降级）"""
        if self.browser is None:
            self.playwright = await async_playwright().start()
            
            # 尝试不同的浏览器配置（优先使用系统浏览器）
            browser_configs = [
                # 优先尝试使用 Chrome
                {
                    'channel': 'chrome',
                    'executable_path': None,
                    'headless': True
                },
                # 尝试使用 Edge
                {
                    'channel': 'msedge',
                    'executable_path': None,
                    'headless': True
                },
                # 最后尝试 Playwright 自带的 Chromium
                {
                    'channel': None,
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
                error_msg = (
                    f"无法启动浏览器。请确保系统已安装 Chrome 或 Edge 浏览器。\n"
                    f"最后一次错误: {str(last_error)[:200]}"
                )
                logger.error(error_msg)
                raise Exception(error_msg)
            
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
    
    async def explore_and_plan(
        self,
        url: str,
        max_depth: int = 2,
        timeout: int = 60,
        mcp_config: Optional[Dict[str, Any]] = None,
        requirements: str = ""
    ) -> Dict[str, Any]:
        """
        探索应用并生成测试计划
        优先使用 MCP Server，失败时降级到本地 Playwright
        
        Args:
            url: 应用URL
            max_depth: 探索深度
            timeout: 超时时间
            mcp_config: MCP配置(可选)
            requirements: 测试需求描述(可选)
            
        Returns:
            测试计划数据
        """
        try:
            logger.info(f"开始探索应用: {url}, 深度: {max_depth}")
            logger.info(f"MCP 配置: {mcp_config}")  # 添加日志
            
            # 1. 优先尝试使用 MCP Server
            if mcp_config:
                try:
                    logger.info(f"尝试使用 MCP Server 进行浏览器探索... URL: {mcp_config.get('url')}")
                    result = await self._explore_with_mcp(url, max_depth, timeout, mcp_config, requirements)
                    logger.info("✓ 使用 MCP Server 完成探索")
                    return result
                except Exception as mcp_error:
                    logger.error(f"MCP Server 探索失败: {str(mcp_error)}", exc_info=True)
                    logger.info("降级到本地 Playwright...")
            else:
                logger.info("未提供 MCP 配置，跳过 MCP Server")
            
            # 2. 降级到本地 Playwright
            try:
                logger.info("尝试使用本地 Playwright...")
                result = await self._explore_with_local_playwright(url, max_depth, timeout)
                logger.info("✓ 使用本地 Playwright 完成探索")
                return result
            except Exception as playwright_error:
                logger.error(f"本地 Playwright 探索失败: {str(playwright_error)}", exc_info=True)
                logger.info("降级到 LLM 推理...")
            
            # 3. 最终降级到 LLM 推理（无浏览器）
            logger.info("使用 LLM 推理模式...")
            result = await self._explore_with_llm(url, max_depth)
            logger.info("✓ 使用 LLM 推理完成探索")
            return result
            
        except Exception as e:
            logger.error(f"探索失败: {str(e)}", exc_info=True)
            raise
    
    async def _explore_with_mcp(
        self,
        url: str,
        max_depth: int,
        timeout: int,
        mcp_config: Dict[str, Any],
        requirements: str = ""
    ) -> Dict[str, Any]:
        """使用 MCP Server 进行真实浏览器探索"""
        try:
            from app.models.playwright_agents import PlaywrightExplorationStep
            
            # 创建 MCP 客户端
            client_config = {
                "n-tester": {
                    "url": mcp_config.get('url', 'http://127.0.0.1:8006'),
                    "transport": "streamable-http"  # 使用 streamable-http
                }
            }
            
            self.mcp_client = MultiServerMCPClient(client_config)
            
            # 用于存储探索步骤
            exploration_steps = []
            
            # 使用 session 上下文管理器
            async with self.mcp_client.session("n-tester") as session:
                # 1. 使用增强工具导航
                logger.info(f"🎭 MCP: 使用增强工具导航到 {url}")
                navigate_result = await session.call_tool(
                    "enhanced_navigate",
                    {
                        "url": url,
                        "wait_until": "networkidle"  # 等待网络空闲，确保页面完全加载
                    }
                )
                
                logger.info(f"✅ 导航完成")
                
                # 2. 获取页面快照（使用官方工具）
                logger.info(f"📸 获取页面快照...")
                snapshot_result = await session.call_tool(
                    "call_playwright_tool",
                    {
                        "tool_name": "browser_snapshot",
                        "arguments": {}
                    }
                )
                
                # 3. 获取截图（使用增强工具）
                logger.info(f"📷 获取页面截图...")
                screenshot_result = await session.call_tool(
                    "enhanced_screenshot",
                    {"full_page": False}
                )
                
                # 4. 获取网络请求（用于分析 API 调用）
                logger.info(f"🌐 获取网络请求...")
                try:
                    network_result = await session.call_tool(
                        "enhanced_get_network_requests",
                        {"include_static": False}
                    )
                except Exception as e:
                    logger.warning(f"获取网络请求失败: {e}")
                    network_result = None
                
                # 5. 获取控制台日志（用于发现错误）
                logger.info(f"📋 获取控制台日志...")
                try:
                    console_result = await session.call_tool(
                        "enhanced_get_console_logs",
                        {"level": "warning"}  # 获取警告和错误
                    )
                except Exception as e:
                    logger.warning(f"获取控制台日志失败: {e}")
                    console_result = None
                
                # 6. 获取导航历史
                logger.info(f"📜 获取导航历史...")
                try:
                    history_result = await session.call_tool(
                        "get_navigation_history",
                        {}
                    )
                except Exception as e:
                    logger.warning(f"获取导航历史失败: {e}")
                    history_result = None
                
                # 提取快照数据
                logger.info(f"📊 解析探索结果...")
                
                # 解析快照
                snapshot = {}
                if isinstance(snapshot_result, dict):
                    result_data = snapshot_result.get('result', {})
                    if isinstance(result_data, dict):
                        snapshot = result_data
                    else:
                        snapshot = snapshot_result
                elif hasattr(snapshot_result, 'content'):
                    content = snapshot_result.content
                    if isinstance(content, list) and len(content) > 0:
                        text_content = content[0].text if hasattr(content[0], 'text') else content[0]
                        if isinstance(text_content, str):
                            try:
                                snapshot = json.loads(text_content)
                            except:
                                snapshot = {"text": text_content}
                
                # 解析截图
                screenshot = ""
                if isinstance(screenshot_result, dict):
                    result_data = screenshot_result.get('result', {})
                    if isinstance(result_data, dict):
                        screenshot = result_data.get('screenshot_after', '')
                    else:
                        screenshot = screenshot_result.get('screenshot', '')
                elif hasattr(screenshot_result, 'content'):
                    content = screenshot_result.content
                    if isinstance(content, list) and len(content) > 0:
                        text_content = content[0].text if hasattr(content[0], 'text') else content[0]
                        if isinstance(text_content, str):
                            try:
                                data = json.loads(text_content)
                                screenshot = data.get('screenshot', '')
                            except:
                                pass
                
                # 添加截图到快照
                if screenshot:
                    snapshot['screenshot'] = screenshot
                
                # 解析网络请求
                network_requests = []
                if network_result:
                    if isinstance(network_result, dict):
                        result_data = network_result.get('result', {})
                        if isinstance(result_data, dict):
                            network_requests = result_data.get('requests', [])
                
                # 解析控制台日志
                console_logs = []
                if console_result:
                    if isinstance(console_result, dict):
                        result_data = console_result.get('result', {})
                        if isinstance(result_data, dict):
                            console_logs = result_data.get('messages', [])
                
                # 解析导航历史
                navigation_history = []
                if history_result:
                    if isinstance(history_result, list):
                        navigation_history = history_result
                    elif isinstance(history_result, dict):
                        navigation_history = history_result.get('result', [])
                
                logger.info(f"✅ MCP 探索完成（使用增强工具）")
                logger.info(f"  - 页面标题: {snapshot.get('title', 'N/A')}")
                logger.info(f"  - URL: {snapshot.get('url', url)}")
                logger.info(f"  - 截图大小: {len(screenshot)} 字符")
                logger.info(f"  - 网络请求: {len(network_requests)} 个")
                logger.info(f"  - 控制台日志: {len(console_logs)} 条")
                logger.info(f"  - 导航历史: {len(navigation_history)} 条")
                
                # 记录探索步骤（增强版）
                step_data = {
                    "step_number": 1,
                    "action": "enhanced_explore",
                    "description": f"使用增强工具探索 {url}（官方 Playwright MCP）",
                    "url": snapshot.get('url', url),
                    "screenshot": screenshot,
                    "page_title": snapshot.get('title'),
                    "elements_found": {
                        "links": len(snapshot.get('links', [])),
                        "buttons": len(snapshot.get('buttons', [])),
                        "inputs": len(snapshot.get('inputs', []))
                    },
                    "network_requests": len(network_requests),
                    "console_logs": len(console_logs),
                    "navigation_history": len(navigation_history),
                    "duration": snapshot.get('duration', 0),
                    "status": "success",
                    "method": "enhanced_tools_with_official_playwright_mcp"
                }
                exploration_steps.append(step_data)
                
                # 添加额外信息到快照
                snapshot['network_requests'] = network_requests[:10]  # 只保留前10个
                snapshot['console_logs'] = console_logs[:20]  # 只保留前20条
                snapshot['navigation_history'] = navigation_history
                
                # 3. 关闭浏览器
                try:
                    await session.call_tool("browser_close", {})
                except:
                    pass
            
            # 4. 使用 LLM 分析页面并生成测试计划
            # 注意：移除截图数据，避免 prompt 过大
            snapshot_for_llm = {k: v for k, v in snapshot.items() if k != 'screenshot'}
            prompt = self._build_exploration_prompt_with_snapshot(url, snapshot_for_llm, max_depth, requirements)
            
            response = await self.llm_service.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_tokens=4000
            )
            
            # 5. 解析测试场景
            test_scenarios = self._parse_test_scenarios(response)
            
            # 5. 格式化测试计划
            plan_content = self._format_test_plan(url, test_scenarios)
            
            return {
                "url": url,
                "max_depth": max_depth,
                "test_scenarios": test_scenarios,
                "exploration_result": {
                    "total_scenarios": len(test_scenarios),
                    "explored_at": datetime.now().isoformat(),
                    "snapshot": snapshot,
                    "method": "mcp_server",
                    "plan_content": plan_content,
                    "exploration_steps": exploration_steps  # 添加探索步骤
                }
            }
            
        except Exception as e:
            logger.error(f"MCP 探索失败: {e}", exc_info=True)
            raise
    
    async def _explore_with_local_playwright(
        self,
        url: str,
        max_depth: int,
        timeout: int
    ) -> Dict[str, Any]:
        """使用本地 Playwright 进行浏览器探索"""
        try:
            # 初始化浏览器
            await self._init_browser()
            
            try:
                # 1. 导航到目标页面
                await self.page.goto(url, wait_until='networkidle', timeout=30000)
                logger.info(f"成功导航到: {url}")
                
                # 2. 获取页面快照
                snapshot = await self._get_page_snapshot()
                logger.info("获取页面快照完成")
                
                # 3. 使用 LLM 分析页面并生成测试计划
                prompt = self._build_exploration_prompt_with_snapshot(url, snapshot, max_depth)
                
                response = await self.llm_service.generate_text(
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=4000
                )
                
                # 4. 解析测试场景
                test_scenarios = self._parse_test_scenarios(response)
                
                # 5. 格式化测试计划
                plan_content = self._format_test_plan(url, test_scenarios)
                
                result = {
                    "url": url,
                    "max_depth": max_depth,
                    "test_scenarios": test_scenarios,
                    "exploration_result": {
                        "total_scenarios": len(test_scenarios),
                        "explored_at": datetime.now().isoformat(),
                        "snapshot": snapshot,
                        "method": "local_playwright",
                        "plan_content": plan_content
                    }
                }
                
                logger.info(f"✓ 探索完成，生成 {len(test_scenarios)} 个测试场景")
                return result
                
            finally:
                # 确保关闭浏览器
                await self._close_browser()
            
        except Exception as e:
            logger.error(f"本地 Playwright 探索失败: {str(e)}")
            # 确保关闭浏览器
            try:
                await self._close_browser()
            except:
                pass
            raise
    
    async def _explore_with_llm(
        self,
        url: str,
        max_depth: int
    ) -> Dict[str, Any]:
        """使用 LLM 推理生成测试计划（无浏览器降级方案）"""
        # 构建探索提示词
        prompt = self._build_exploration_prompt_with_snapshot(url, {}, max_depth)
        
        # 调用LLM生成测试计划
        response = await self.llm_service.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=4000
        )
        
        # 解析测试场景
        test_scenarios = self._parse_test_scenarios(response)
        
        # 格式化测试计划
        plan_content = self._format_test_plan(url, test_scenarios)
        
        return {
            "url": url,
            "max_depth": max_depth,
            "test_scenarios": test_scenarios,
            "exploration_result": {
                "total_scenarios": len(test_scenarios),
                "explored_at": datetime.now().isoformat(),
                "method": "llm_inference",
                "plan_content": plan_content
            }
        }
    
    async def _get_page_snapshot(self) -> Dict[str, Any]:
        """获取页面快照"""
        try:
            # 获取页面基本信息
            title = await self.page.title()
            url = self.page.url
            
            # 获取页面文本内容（限制长度）
            text_content = await self.page.evaluate('''
                () => {
                    return document.body.innerText.substring(0, 2000);
                }
            ''')
            
            # 获取所有链接
            links = await self.page.evaluate('''
                () => {
                    const links = Array.from(document.querySelectorAll('a'));
                    return links.slice(0, 20).map(a => ({
                        text: a.innerText.trim(),
                        href: a.href
                    })).filter(link => link.text && link.href);
                }
            ''')
            
            # 获取所有按钮
            buttons = await self.page.evaluate('''
                () => {
                    const buttons = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]'));
                    return buttons.slice(0, 20).map(btn => ({
                        text: btn.innerText || btn.value || '',
                        type: btn.type || 'button'
                    })).filter(btn => btn.text);
                }
            ''')
            
            # 获取所有输入框
            inputs = await self.page.evaluate('''
                () => {
                    const inputs = Array.from(document.querySelectorAll('input, textarea'));
                    return inputs.slice(0, 20).map(input => ({
                        type: input.type || 'text',
                        name: input.name || '',
                        placeholder: input.placeholder || ''
                    }));
                }
            ''')
            
            # 获取表单
            forms = await self.page.evaluate('''
                () => {
                    const forms = Array.from(document.querySelectorAll('form'));
                    return forms.slice(0, 10).map(form => ({
                        action: form.action || '',
                        method: form.method || 'GET',
                        inputs: Array.from(form.querySelectorAll('input, textarea')).length
                    }));
                }
            ''')
            
            return {
                "title": title,
                "url": url,
                "text_content": text_content,
                "links": links,
                "buttons": buttons,
                "inputs": inputs,
                "forms": forms
            }
            
        except Exception as e:
            logger.error(f"获取页面快照失败: {str(e)}")
            return {"error": f"获取快照失败: {str(e)}"}
    
    def _build_exploration_prompt_with_snapshot(self, url: str, snapshot: Dict, max_depth: int, requirements: str = "") -> str:
        """构建基于页面快照的探索提示词"""
        
        # 如果有测试需求描述，添加到 prompt 中
        requirements_section = ""
        if requirements:
            requirements_section = f"""

**用户测试需求:**
{requirements}

请特别关注用户提出的测试需求，确保生成的测试场景能够覆盖这些需求。
"""
        
        return f"""
你是一位专业的 Web 测试规划专家，在质量保证、用户体验测试和测试场景设计方面拥有丰富的经验。

应用URL: {url}
探索深度: {max_depth}层
{requirements_section}
页面快照信息:
{json.dumps(snapshot, indent=2, ensure_ascii=False)}

请基于页面快照分析这个应用，并生成详细的测试场景。每个测试场景应包含：
1. 清晰、描述性的标题
2. 详细的分步说明
3. 适当的预期结果
4. 关于起始状态的假设（始终假设空白/全新状态）
5. 成功标准和失败条件

测试场景应涵盖：
- 正常路径场景（正常用户行为）
- 边缘案例和边界条件
- 错误处理和验证

请以JSON格式返回：
{{
    "test_scenarios": [
        {{
            "name": "场景名称",
            "description": "场景描述",
            "priority": "high/medium/low",
            "seed_file": "tests/seed.spec.ts",
            "steps": [
                "步骤1",
                "步骤2"
            ],
            "expected_result": "预期结果",
            "assumptions": ["假设1", "假设2"]
        }}
    ]
}}

请生成至少5个不同的测试场景，确保场景是独立的，可以按任何顺序运行。
"""
    
    def _format_test_plan(self, url: str, test_scenarios: List[Dict]) -> str:
        """格式化测试计划为 Markdown"""
        content = f"""# 测试计划

**应用URL:** {url}
**生成时间:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 测试场景

"""
        for idx, scenario in enumerate(test_scenarios, 1):
            content += f"""### {idx}. {scenario.get('name', '未命名场景')}

**描述:** {scenario.get('description', '')}
**优先级:** {scenario.get('priority', 'medium')}
**种子文件:** {scenario.get('seed_file', 'tests/seed.spec.ts')}

**步骤:**
"""
            for step_idx, step in enumerate(scenario.get('steps', []), 1):
                content += f"{step_idx}. {step}\n"
            
            content += f"\n**预期结果:** {scenario.get('expected_result', '')}\n\n"
            
            if scenario.get('assumptions'):
                content += "**假设:**\n"
                for assumption in scenario['assumptions']:
                    content += f"- {assumption}\n"
                content += "\n"
        
        return content
    
    def _parse_test_scenarios(self, response: str) -> List[Dict[str, Any]]:
        """解析测试场景"""
        import json
        import re
        
        try:
            # 尝试直接解析JSON
            data = json.loads(response)
            return data.get("test_scenarios", [])
        except json.JSONDecodeError:
            # 如果解析失败，尝试提取JSON部分
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    return data.get("test_scenarios", [])
                except:
                    pass
            
            # 如果仍然失败，返回默认场景
            logger.warning("无法解析LLM响应，返回默认测试场景")
            return self._get_default_scenarios()
    
    def _get_default_scenarios(self) -> List[Dict[str, Any]]:
        """获取默认测试场景"""
        return [
            {
                "name": "页面加载测试",
                "description": "验证页面能够正常加载",
                "priority": "high",
                "steps": [
                    "访问应用首页",
                    "等待页面加载完成",
                    "验证页面标题和主要元素"
                ],
                "expected_result": "页面成功加载，所有主要元素可见"
            },
            {
                "name": "导航功能测试",
                "description": "验证页面导航功能正常",
                "priority": "medium",
                "steps": [
                    "点击导航菜单",
                    "验证页面跳转",
                    "检查URL变化"
                ],
                "expected_result": "导航功能正常，页面正确跳转"
            },
            {
                "name": "表单提交测试",
                "description": "验证表单能够正常提交",
                "priority": "high",
                "steps": [
                    "填写表单字段",
                    "点击提交按钮",
                    "验证提交结果"
                ],
                "expected_result": "表单成功提交，显示成功消息"
            }
        ]
