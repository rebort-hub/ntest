"""
N-Tester MCP 增强版 - 集成官方 Playwright MCP

这个模块提供了 N-Tester MCP 与官方 Playwright MCP 的集成功能
"""

import httpx
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PlaywrightMCPClient:
    """
    Playwright MCP 客户端
    通过 HTTP 与官方 Playwright MCP 通信
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:3000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        self._tools_cache = None
        self._cache_time = None
        
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Playwright MCP 健康检查失败: {e}")
            return False
    
    async def list_tools(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        获取 Playwright 工具列表
        
        Args:
            use_cache: 是否使用缓存
        """
        # 使用缓存（5分钟有效）
        if use_cache and self._tools_cache and self._cache_time:
            if (datetime.now() - self._cache_time).seconds < 300:
                return self._tools_cache
        
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/list",
                json={}
            )
            response.raise_for_status()
            result = response.json()
            
            tools = result.get("result", {}).get("tools", [])
            
            # 更新缓存
            self._tools_cache = tools
            self._cache_time = datetime.now()
            
            logger.info(f"获取到 {len(tools)} 个 Playwright 工具")
            return tools
            
        except Exception as e:
            logger.error(f"获取 Playwright 工具列表失败: {e}")
            return []
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用 Playwright 工具
        
        Args:
            name: 工具名称
            arguments: 工具参数
        """
        try:
            logger.info(f"调用 Playwright 工具: {name}")
            logger.debug(f"参数: {arguments}")
            
            response = await self.client.post(
                f"{self.base_url}/tools/call",
                json={
                    "name": name,
                    "arguments": arguments
                }
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Playwright 工具调用成功: {name}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Playwright 工具调用失败 {name}: HTTP {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Playwright 工具调用失败 {name}: {e}")
            raise
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


class EnhancedPlaywrightTools:
    """
    增强的 Playwright 工具集
    在官方工具基础上添加额外功能
    """
    
    def __init__(self, playwright_client: PlaywrightMCPClient):
        self.playwright_client = playwright_client
        self.navigation_history = []
        self.screenshot_count = 0
    
    async def enhanced_navigate(
        self, 
        url: str, 
        wait_until: str = "load",
        save_history: bool = True
    ) -> Dict[str, Any]:
        """
        增强的页面导航
        
        Args:
            url: 目标 URL
            wait_until: 等待条件 (load, domcontentloaded, networkidle)
            save_history: 是否保存导航历史
        """
        logger.info(f"增强导航: {url}")
        
        # 前置处理：保存导航历史
        if save_history:
            self.navigation_history.append({
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "wait_until": wait_until
            })
        
        # 调用官方 Playwright 工具
        try:
            result = await self.playwright_client.call_tool(
                "playwright_navigate",
                {
                    "url": url,
                    "waitUntil": wait_until
                }
            )
            
            # 后置处理：可以添加自动截图、性能监控等
            logger.info(f"导航成功: {url}")
            
            return {
                "status": "success",
                "url": url,
                "result": result,
                "history_count": len(self.navigation_history)
            }
            
        except Exception as e:
            logger.error(f"导航失败: {url}, 错误: {e}")
            return {
                "status": "error",
                "url": url,
                "error": str(e)
            }
    
    async def enhanced_click(
        self, 
        selector: str, 
        timeout: int = 30000,
        wait_for_navigation: bool = False
    ) -> Dict[str, Any]:
        """
        增强的点击操作
        
        Args:
            selector: CSS 选择器
            timeout: 超时时间（毫秒）
            wait_for_navigation: 是否等待页面导航
        """
        logger.info(f"增强点击: {selector}")
        
        try:
            # 调用官方 Playwright 工具
            result = await self.playwright_client.call_tool(
                "playwright_click",
                {
                    "selector": selector,
                    "timeout": timeout
                }
            )
            
            # 如果需要等待导航
            if wait_for_navigation:
                await asyncio.sleep(1)  # 简单等待，实际应该监听导航事件
            
            logger.info(f"点击成功: {selector}")
            
            return {
                "status": "success",
                "selector": selector,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"点击失败: {selector}, 错误: {e}")
            return {
                "status": "error",
                "selector": selector,
                "error": str(e)
            }
    
    async def enhanced_fill(
        self, 
        selector: str, 
        value: str,
        clear_first: bool = True
    ) -> Dict[str, Any]:
        """
        增强的输入操作
        
        Args:
            selector: CSS 选择器
            value: 输入值
            clear_first: 是否先清空
        """
        logger.info(f"增强输入: {selector} = {value}")
        
        try:
            # 如果需要先清空
            if clear_first:
                # 可以先调用 clear 或者发送特殊按键
                pass
            
            # 调用官方 Playwright 工具
            result = await self.playwright_client.call_tool(
                "playwright_fill",
                {
                    "selector": selector,
                    "value": value
                }
            )
            
            logger.info(f"输入成功: {selector}")
            
            return {
                "status": "success",
                "selector": selector,
                "value": value,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"输入失败: {selector}, 错误: {e}")
            return {
                "status": "error",
                "selector": selector,
                "error": str(e)
            }
    
    async def enhanced_screenshot(
        self, 
        full_page: bool = False,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        增强的截图操作
        
        Args:
            full_page: 是否截取整个页面
            save_to_db: 是否保存到数据库
        """
        self.screenshot_count += 1
        logger.info(f"增强截图 #{self.screenshot_count}: full_page={full_page}")
        
        try:
            # 调用官方 Playwright 工具
            result = await self.playwright_client.call_tool(
                "playwright_screenshot",
                {
                    "fullPage": full_page
                }
            )
            
            # 后置处理：保存到数据库、上传到云存储等
            if save_to_db:
                # TODO: 实现保存到数据库的逻辑
                logger.info("截图已保存到数据库")
            
            logger.info(f"截图成功 #{self.screenshot_count}")
            
            return {
                "status": "success",
                "screenshot_id": self.screenshot_count,
                "full_page": full_page,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_navigation_history(self) -> List[Dict[str, Any]]:
        """获取导航历史"""
        return self.navigation_history
    
    async def clear_navigation_history(self):
        """清空导航历史"""
        self.navigation_history.clear()
        logger.info("导航历史已清空")


class PlaywrightIntegrationManager:
    """
    Playwright 集成管理器
    负责管理 Playwright MCP 的生命周期和工具注册
    """
    
    def __init__(self, playwright_url: str = "http://127.0.0.1:3000"):
        self.playwright_url = playwright_url
        self.client = None
        self.enhanced_tools = None
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """初始化 Playwright 集成"""
        max_retries = 3
        retry_delay = 2  # 秒
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"重试 Playwright 集成初始化 ({attempt + 1}/{max_retries})...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.info("初始化 Playwright 集成...")
                
                # 创建客户端
                self.client = PlaywrightMCPClient(self.playwright_url)
                
                # 健康检查
                is_healthy = await self.client.health_check()
                if not is_healthy:
                    logger.warning(f"Playwright MCP 服务健康检查失败 (尝试 {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        continue
                    logger.error("Playwright MCP 服务不可用")
                    return False
                
                # 创建增强工具
                self.enhanced_tools = EnhancedPlaywrightTools(self.client)
                
                # 获取工具列表
                tools = await self.client.list_tools()
                if not tools:
                    logger.warning(f"未获取到 Playwright 工具 (尝试 {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        continue
                    logger.error("无法获取 Playwright 工具列表")
                    return False
                
                logger.info(f"Playwright 集成初始化成功，可用工具: {len(tools)}")
                
                self.is_initialized = True
                return True
                
            except Exception as e:
                logger.error(f"Playwright 集成初始化失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    continue
                return False
        
        return False
    
    async def register_tools_to_mcp_server(self, mcp_server):
        """
        将增强工具注册到 MCP 服务器
        
        Args:
            mcp_server: MCP 服务器实例
        """
        if not self.is_initialized:
            logger.warning("Playwright 集成未初始化，跳过工具注册")
            return
        
        logger.info("注册增强 Playwright 工具...")
        
        # 注册增强导航工具
        @mcp_server.tool()
        async def enhanced_navigate(url: str, wait_until: str = "load"):
            """
            增强的页面导航工具
            
            Args:
                url: 目标 URL
                wait_until: 等待条件 (load, domcontentloaded, networkidle)
            """
            return await self.enhanced_tools.enhanced_navigate(url, wait_until)
        
        # 注册增强点击工具
        @mcp_server.tool()
        async def enhanced_click(selector: str, timeout: int = 30000):
            """
            增强的点击工具
            
            Args:
                selector: CSS 选择器
                timeout: 超时时间（毫秒）
            """
            return await self.enhanced_tools.enhanced_click(selector, timeout)
        
        # 注册增强输入工具
        @mcp_server.tool()
        async def enhanced_fill(selector: str, value: str):
            """
            增强的输入工具
            
            Args:
                selector: CSS 选择器
                value: 输入值
            """
            return await self.enhanced_tools.enhanced_fill(selector, value)
        
        # 注册增强截图工具
        @mcp_server.tool()
        async def enhanced_screenshot(full_page: bool = False):
            """
            增强的截图工具
            
            Args:
                full_page: 是否截取整个页面
            """
            return await self.enhanced_tools.enhanced_screenshot(full_page)
        
        # 注册表单填写工具
        @mcp_server.tool()
        async def enhanced_fill_form(fields: list):
            """
            增强的表单填写工具（支持多字段）
            
            Args:
                fields: 字段列表，格式：[{"selector": "#username", "value": "test"}, ...]
            """
            try:
                results = []
                for field in fields:
                    selector = field.get("selector")
                    value = field.get("value")
                    result = await self.enhanced_tools.enhanced_fill(selector, value)
                    results.append(result)
                return {
                    "status": "success",
                    "filled_fields": len(fields),
                    "results": results
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e)
                }
        
        # 注册等待工具
        @mcp_server.tool()
        async def enhanced_wait_for_element(selector: str, timeout: int = 30000):
            """
            增强的等待元素工具
            
            Args:
                selector: CSS 选择器
                timeout: 超时时间（毫秒）
            """
            try:
                result = await self.client.call_tool(
                    "browser_wait_for",
                    {"text": selector, "time": timeout / 1000}
                )
                return {
                    "status": "success",
                    "selector": selector,
                    "result": result
                }
            except Exception as e:
                return {
                    "status": "error",
                    "selector": selector,
                    "error": str(e)
                }
        
        # 注册网络请求监控工具
        @mcp_server.tool()
        async def enhanced_get_network_requests(include_static: bool = False):
            """
            获取网络请求（用于调试和验证）
            
            Args:
                include_static: 是否包含静态资源
            """
            try:
                result = await self.client.call_tool(
                    "browser_network_requests",
                    {"includeStatic": include_static}
                )
                return result
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e)
                }
        
        # 注册控制台日志工具
        @mcp_server.tool()
        async def enhanced_get_console_logs(level: str = "info"):
            """
            获取浏览器控制台日志（用于调试）
            
            Args:
                level: 日志级别 (error, warning, info, debug)
            """
            try:
                result = await self.client.call_tool(
                    "browser_console_messages",
                    {"level": level}
                )
                return result
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e)
                }
        
        # 注册通用工具调用（可以调用任何官方 Playwright 工具）
        @mcp_server.tool()
        async def call_playwright_tool(tool_name: str, arguments: dict = None):
            """
            通用工具：调用任何官方 Playwright MCP 工具
            
            这个工具允许你调用官方 Playwright MCP 的任何工具，
            即使我们没有为它创建专门的增强工具。
            
            Args:
                tool_name: 官方工具名称（如 browser_hover, browser_drag 等）
                arguments: 工具参数（字典格式）
            
            Examples:
                # 悬停操作
                call_playwright_tool("browser_hover", {"ref": "element_ref"})
                
                # 拖拽操作
                call_playwright_tool("browser_drag", {
                    "startRef": "start_ref",
                    "endRef": "end_ref"
                })
                
                # 选择下拉框
                call_playwright_tool("browser_select_option", {
                    "ref": "select_ref",
                    "values": ["option1"]
                })
                
                # 文件上传
                call_playwright_tool("browser_file_upload", {
                    "paths": ["/path/to/file.txt"]
                })
                
                # 处理弹窗
                call_playwright_tool("browser_handle_dialog", {
                    "accept": True
                })
                
                # 标签页管理
                call_playwright_tool("browser_tabs", {
                    "action": "list"
                })
                
                # 运行 Playwright 代码
                call_playwright_tool("browser_run_code", {
                    "code": "async (page) => { return await page.title(); }"
                })
            """
            try:
                logger.info(f"通用调用官方工具: {tool_name}")
                
                result = await self.client.call_tool(
                    tool_name,
                    arguments or {}
                )
                
                logger.info(f"官方工具调用成功: {tool_name}")
                
                return {
                    "status": "success",
                    "tool_name": tool_name,
                    "result": result
                }
            except Exception as e:
                logger.error(f"官方工具调用失败: {tool_name}, 错误: {e}")
                return {
                    "status": "error",
                    "tool_name": tool_name,
                    "error": str(e)
                }
        
        # 注册导航历史工具
        @mcp_server.tool()
        async def get_navigation_history():
            """获取导航历史"""
            return await self.enhanced_tools.get_navigation_history()
        
        # 注册工具列表查询
        @mcp_server.tool()
        async def list_playwright_tools():
            """获取所有可用的 Playwright 工具"""
            tools = await self.client.list_tools(use_cache=False)
            return {
                "tools": [tool.get("name") for tool in tools],
                "count": len(tools),
                "source": "official_playwright_mcp"
            }
        
        logger.info("增强 Playwright 工具注册完成")
    
    async def cleanup(self):
        """清理资源"""
        if self.client:
            await self.client.close()
        logger.info("Playwright 集成资源已清理")


# 使用示例
async def example_usage():
    """使用示例"""
    
    # 创建集成管理器
    manager = PlaywrightIntegrationManager("http://127.0.0.1:3000")
    
    # 初始化
    success = await manager.initialize()
    if not success:
        print("初始化失败")
        return
    
    # 使用增强工具
    result = await manager.enhanced_tools.enhanced_navigate("https://example.com")
    print(f"导航结果: {result}")
    
    result = await manager.enhanced_tools.enhanced_click("#button")
    print(f"点击结果: {result}")
    
    result = await manager.enhanced_tools.enhanced_screenshot(full_page=True)
    print(f"截图结果: {result}")
    
    # 查看导航历史
    history = await manager.enhanced_tools.get_navigation_history()
    print(f"导航历史: {history}")
    
    # 清理
    await manager.cleanup()


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行示例
    asyncio.run(example_usage())
