"""
N-Tester MCP 增强版配置文件
"""

import os
from typing import Optional


class EnhancedConfig:
    """增强版配置"""
    
    # ==================== N-Tester MCP 基础配置 ====================
    
    # 服务配置
    HOST: str = os.getenv("N_TESTER_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("N_TESTER_PORT", "8006"))
    
    # API 密钥
    API_KEY: str = os.getenv("N-Tester_API_KEY", "N-Tester-default-mcp-key-2025")
    
    # ==================== Playwright MCP 集成配置 ====================
    
    # 是否启用 Playwright 集成
    ENABLE_PLAYWRIGHT_INTEGRATION: bool = os.getenv(
        "ENABLE_PLAYWRIGHT_INTEGRATION", "true"
    ).lower() == "true"
    
    # Playwright MCP 连接模式: "http" 或 "stdio"
    PLAYWRIGHT_MODE: str = os.getenv("PLAYWRIGHT_MODE", "http")
    
    # Playwright MCP HTTP 地址（当 mode=http 时使用）
    PLAYWRIGHT_HTTP_URL: str = os.getenv(
        "PLAYWRIGHT_HTTP_URL", "http://127.0.0.1:3000"
    )
    
    # Playwright MCP 命令（当 mode=stdio 时使用）
    PLAYWRIGHT_COMMAND: str = os.getenv("PLAYWRIGHT_COMMAND", "npx")
    PLAYWRIGHT_ARGS: list = ["@playwright/mcp-server"]
    
    # ==================== 功能开关 ====================
    
    # 是否启用增强工具
    ENABLE_ENHANCED_TOOLS: bool = os.getenv(
        "ENABLE_ENHANCED_TOOLS", "true"
    ).lower() == "true"
    
    # 是否启用导航历史记录
    ENABLE_NAVIGATION_HISTORY: bool = os.getenv(
        "ENABLE_NAVIGATION_HISTORY", "true"
    ).lower() == "true"
    
    # 是否自动保存截图到数据库
    AUTO_SAVE_SCREENSHOTS: bool = os.getenv(
        "AUTO_SAVE_SCREENSHOTS", "false"
    ).lower() == "true"
    
    # ==================== 性能配置 ====================
    
    # 工具调用超时时间（秒）
    TOOL_CALL_TIMEOUT: int = int(os.getenv("TOOL_CALL_TIMEOUT", "60"))
    
    # Playwright 工具列表缓存时间（秒）
    TOOLS_CACHE_TTL: int = int(os.getenv("TOOLS_CACHE_TTL", "300"))
    
    # 最大导航历史记录数
    MAX_NAVIGATION_HISTORY: int = int(os.getenv("MAX_NAVIGATION_HISTORY", "100"))
    
    # ==================== 日志配置 ====================
    
    # 日志级别: DEBUG, INFO, WARNING, ERROR
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # 日志文件路径
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", "n-tester-mcp-enhanced.log")
    
    # 是否启用性能日志
    ENABLE_PERFORMANCE_LOG: bool = os.getenv(
        "ENABLE_PERFORMANCE_LOG", "true"
    ).lower() == "true"
    
    # ==================== 健康检查配置 ====================
    
    # 启动时是否检查 Playwright MCP 健康状态
    CHECK_PLAYWRIGHT_HEALTH_ON_STARTUP: bool = os.getenv(
        "CHECK_PLAYWRIGHT_HEALTH_ON_STARTUP", "true"
    ).lower() == "true"
    
    # 健康检查超时时间（秒）
    HEALTH_CHECK_TIMEOUT: int = int(os.getenv("HEALTH_CHECK_TIMEOUT", "10"))
    
    # 健康检查重试次数
    HEALTH_CHECK_RETRIES: int = int(os.getenv("HEALTH_CHECK_RETRIES", "3"))
    
    # ==================== 工具映射策略 ====================
    
    # 需要增强的工具列表（其他工具将透传）
    ENHANCED_TOOLS: list = [
        "navigate",
        "click", 
        "fill",
        "screenshot"
    ]
    
    # 透传的工具列表（直接调用官方工具，不做增强）
    PASSTHROUGH_TOOLS: list = [
        "evaluate",
        "wait_for_selector",
        "get_attribute"
    ]
    
    @classmethod
    def validate(cls) -> bool:
        """验证配置"""
        errors = []
        
        # 验证端口
        if not (1 <= cls.PORT <= 65535):
            errors.append(f"无效的端口号: {cls.PORT}")
        
        # 验证 Playwright 模式
        if cls.PLAYWRIGHT_MODE not in ["http", "stdio"]:
            errors.append(f"无效的 Playwright 模式: {cls.PLAYWRIGHT_MODE}")
        
        # 验证日志级别
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if cls.LOG_LEVEL.upper() not in valid_log_levels:
            errors.append(f"无效的日志级别: {cls.LOG_LEVEL}")
        
        if errors:
            for error in errors:
                print(f"❌ 配置错误: {error}")
            return False
        
        return True
    
    @classmethod
    def print_config(cls):
        """打印当前配置"""
        print("=" * 60)
        print("N-Tester MCP 增强版配置")
        print("=" * 60)
        print(f"服务地址:           {cls.HOST}:{cls.PORT}")
        print(f"Playwright 集成:    {'启用' if cls.ENABLE_PLAYWRIGHT_INTEGRATION else '禁用'}")
        print(f"Playwright 模式:    {cls.PLAYWRIGHT_MODE}")
        if cls.PLAYWRIGHT_MODE == "http":
            print(f"Playwright URL:     {cls.PLAYWRIGHT_HTTP_URL}")
        print(f"增强工具:           {'启用' if cls.ENABLE_ENHANCED_TOOLS else '禁用'}")
        print(f"导航历史:           {'启用' if cls.ENABLE_NAVIGATION_HISTORY else '禁用'}")
        print(f"日志级别:           {cls.LOG_LEVEL}")
        print(f"日志文件:           {cls.LOG_FILE or '禁用'}")
        print("=" * 60)


# 环境变量配置示例
"""
# .env 文件示例

# N-Tester MCP 基础配置
N_TESTER_HOST=127.0.0.1
N_TESTER_PORT=8006
N-Tester_API_KEY=your-api-key-here

# Playwright 集成配置
ENABLE_PLAYWRIGHT_INTEGRATION=true
PLAYWRIGHT_MODE=http
PLAYWRIGHT_HTTP_URL=http://127.0.0.1:3000

# 功能开关
ENABLE_ENHANCED_TOOLS=true
ENABLE_NAVIGATION_HISTORY=true
AUTO_SAVE_SCREENSHOTS=false

# 性能配置
TOOL_CALL_TIMEOUT=60
TOOLS_CACHE_TTL=300
MAX_NAVIGATION_HISTORY=100

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=n-tester-mcp-enhanced.log
ENABLE_PERFORMANCE_LOG=true

# 健康检查配置
CHECK_PLAYWRIGHT_HEALTH_ON_STARTUP=true
HEALTH_CHECK_TIMEOUT=10
HEALTH_CHECK_RETRIES=3
"""


if __name__ == "__main__":
    # 验证并打印配置
    if EnhancedConfig.validate():
        EnhancedConfig.print_config()
    else:
        print("配置验证失败")
