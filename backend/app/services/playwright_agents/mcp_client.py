"""
MCP Client
"""
import logging
import asyncio
import json
from typing import Dict, Any, List, Optional
import subprocess
import httpx

logger = logging.getLogger(__name__)


class PlaywrightMCPClient:
    """Playwright MCP 客户端"""
    
    def __init__(self, server_config: Optional[Dict[str, Any]] = None):
        """
        初始化 MCP 客户端
        
        Args:
            server_config: MCP Server 配置
                - type: 'stdio' 或 'http'
                - command: 启动命令（stdio模式）
                - args: 命令参数（stdio模式）
                - url: HTTP地址（http模式）
        """
        self.server_config = server_config or self._get_default_config()
        self.process = None
        self.http_client = None
        self.initialized = False
        self.server_type = self.server_config.get('type', 'stdio')
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        # 默认使用 HTTP 方式连接到 N-Tester_MCP
        # FastMCP streamable-http 的基础 URL 不需要 /mcp 后缀
        return {
            'type': 'http',
            'url': 'http://127.0.0.1:8006'
        }
    
    async def initialize(self):
        """初始化 MCP 服务器连接"""
        if self.initialized:
            return
        
        try:
            if self.server_type == 'stdio':
                await self._initialize_stdio()
            elif self.server_type == 'http':
                await self._initialize_http()
            else:
                raise ValueError(f"不支持的 MCP Server 类型: {self.server_type}")
            
            self.initialized = True
            logger.info(f"MCP Server 已连接 ({self.server_type} 模式)")
            
        except Exception as e:
            logger.error(f"初始化 MCP Server 失败: {str(e)}")
            raise
    
    async def _initialize_stdio(self):
        """初始化 STDIO 模式的 MCP Server"""
        command = self.server_config.get('command')
        args = self.server_config.get('args', [])
        
        if not command:
            raise ValueError("STDIO 模式需要提供 command 参数")
        
        # 启动 MCP Server 进程
        self.process = await asyncio.create_subprocess_exec(
            command, *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        logger.info(f"MCP Server 进程已启动: {command} {' '.join(args)}")
    
    async def _initialize_http(self):
        """初始化 HTTP 模式的 MCP Server"""
        url = self.server_config.get('url')
        
        if not url:
            raise ValueError("HTTP 模式需要提供 url 参数")
        
        # 去掉末尾的斜杠，避免重定向问题
        url = url.rstrip('/')
        
        # 创建 HTTP 客户端
        self.http_client = httpx.AsyncClient(
            base_url=url,
            timeout=60.0,
            follow_redirects=True  # 自动跟随重定向
        )
        
        # 测试连接 - FastMCP 的 /mcp 端点
        try:
            response = await self.http_client.get(
                '/mcp',
                headers={'Accept': 'application/json, text/event-stream'}
            )
            logger.info(f"MCP Server HTTP 连接成功: {url}")
        except Exception as e:
            logger.warning(f"MCP Server 连接测试失败，但继续尝试: {str(e)}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用 MCP 工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            if self.server_type == 'stdio':
                return await self._call_tool_stdio(tool_name, arguments)
            elif self.server_type == 'http':
                return await self._call_tool_http(tool_name, arguments)
            else:
                raise ValueError(f"不支持的 MCP Server 类型: {self.server_type}")
                
        except Exception as e:
            logger.error(f"调用 MCP 工具失败: {str(e)}")
            raise
    
    async def _call_tool_stdio(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """通过 STDIO 调用 MCP 工具"""
        # 构建 MCP 请求
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        # 发送请求
        request_json = json.dumps(request) + '\n'
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # 读取响应
        response_line = await self.process.stdout.readline()
        response = json.loads(response_line.decode())
        
        if 'error' in response:
            raise Exception(f"MCP 工具调用失败: {response['error']}")
        
        return response.get('result', {})
    
    async def _call_tool_http(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """通过 HTTP 调用 MCP 工具（FastMCP streamable-http 格式）"""
        try:
            # FastMCP streamable-http 需要同时接受 JSON 和 SSE
            request_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # FastMCP 的端点是 /mcp
            # 需要设置正确的 Accept headers
            response = await self.http_client.post(
                '/mcp',
                json=request_data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json, text/event-stream'
                },
                follow_redirects=True
            )
            response.raise_for_status()
            
            result = response.json()
            
            if 'error' in result:
                raise Exception(f"MCP 工具调用失败: {result['error']}")
            
            return result.get('result', {})
            
        except Exception as e:
            logger.error(f"HTTP MCP 调用失败: {str(e)}")
            raise
    
    async def close(self):
        """关闭 MCP 连接"""
        if self.server_type == 'stdio' and self.process:
            self.process.terminate()
            await self.process.wait()
        elif self.server_type == 'http' and self.http_client:
            await self.http_client.aclose()
        
        self.initialized = False
        logger.info("MCP Server 连接已关闭")


# 全局 MCP 客户端实例
_mcp_client: Optional[PlaywrightMCPClient] = None


async def get_mcp_client(server_config: Optional[Dict[str, Any]] = None) -> PlaywrightMCPClient:
    """
    获取 MCP 客户端实例
    
    Args:
        server_config: MCP Server 配置，如果为 None 则使用默认配置
    """
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = PlaywrightMCPClient(server_config)
        await _mcp_client.initialize()
    return _mcp_client


async def cleanup_mcp_client():
    """清理 MCP 客户端"""
    global _mcp_client
    if _mcp_client:
        await _mcp_client.close()
        _mcp_client = None
