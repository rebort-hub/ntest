"""
启动 N-Tester_MCP HTTP Wrapper
提供简单的 REST API 访问浏览器工具
"""
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入并运行 http_wrapper
if __name__ == "__main__":
    from http_wrapper import app
    import uvicorn
    
    print("=" * 60)
    print("N-Tester MCP HTTP Wrapper")
    print("=" * 60)
    print("启动 HTTP API 服务...")
    print("端口: 8080")
    print("文档: http://0.0.0.0:8080/docs")
    print("健康检查: http://0.0.0.0:8080/health")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
