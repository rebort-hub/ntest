#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "  N-Tester MCP 增强版启动脚本"
echo "  集成官方 Playwright MCP"
echo "========================================"
echo ""

# 获取脚本所在目录的父目录的父目录（N-Tester_MCP 根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/../.." && pwd )"
cd "$ROOT_DIR"

echo -e "${BLUE}[步骤 1/3] 检查环境...${NC}"
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED} 错误: 未找到 Node.js${NC}"
    echo "   请先安装 Node.js: https://nodejs.org/"
    exit 1
fi

# 检查 Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED} 错误: 未找到 Python${NC}"
    echo "   请先安装 Python 3.8+"
    exit 1
fi

# 使用 python3 或 python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo -e "${GREEN} 环境检查通过${NC}"
echo ""

echo -e "${BLUE}[步骤 2/3] 启动 Playwright MCP HTTP 桥接服务...${NC}"
echo ""

# 检查桥接脚本
if [ ! -f "src/integrations/playwright/http_bridge.js" ]; then
    echo -e "${RED} 错误: 未找到 src/integrations/playwright/http_bridge.js${NC}"
    exit 1
fi

# 启动 Playwright MCP 桥接服务（后台）
node src/integrations/playwright/http_bridge.js &
PLAYWRIGHT_PID=$!

echo -e "${GREEN} Playwright MCP 桥接服务已启动 (PID: $PLAYWRIGHT_PID)${NC}"
echo "   监听地址: http://127.0.0.1:3000"
echo ""

# 等待服务启动
echo "等待 Playwright MCP 服务启动..."
sleep 5

# 检查服务是否正常运行
if ! kill -0 $PLAYWRIGHT_PID 2>/dev/null; then
    echo -e "${RED} 错误: Playwright MCP 服务启动失败${NC}"
    exit 1
fi

echo -e "${BLUE}[步骤 3/3] 启动 N-Tester MCP 服务...${NC}"
echo ""

# 检查 N-Tester MCP 主文件
if [ ! -f "src/core/N-Tester_tools.py" ]; then
    echo -e "${RED} 错误: 未找到 src/core/N-Tester_tools.py${NC}"
    exit 1
fi

# 启动 N-Tester MCP 服务（后台）
$PYTHON_CMD src/wrappers/start_http_wrapper.py &
NTESTER_PID=$!

echo -e "${GREEN} N-Tester MCP 服务已启动 (PID: $NTESTER_PID)${NC}"
echo "   监听地址: http://127.0.0.1:8006"
echo ""

echo "========================================"
echo -e "  ${GREEN} 所有服务已启动！${NC}"
echo "========================================"
echo ""
echo "   Playwright MCP: http://127.0.0.1:3000"
echo "   N-Tester MCP:   http://127.0.0.1:8006"
echo ""
echo "  提示:"
echo "   - 服务在后台运行"
echo "   - 按 Ctrl+C 停止所有服务"
echo "   - 查看日志了解服务运行状态"
echo ""

# 保存 PID 到文件
echo $PLAYWRIGHT_PID > /tmp/playwright-mcp.pid
echo $NTESTER_PID > /tmp/ntester-mcp.pid

# 等待用户中断
trap "echo ''; echo '正在停止服务...'; kill $PLAYWRIGHT_PID $NTESTER_PID 2>/dev/null; rm -f /tmp/playwright-mcp.pid /tmp/ntester-mcp.pid; echo '服务已停止'; exit 0" INT TERM

# 保持脚本运行
wait
