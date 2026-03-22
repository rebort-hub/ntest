#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "  停止 N-Tester MCP 服务"
echo "========================================"
echo ""

echo -e "${YELLOW}[1/2] 停止 Playwright MCP 桥接服务...${NC}"

# 检查 PID 文件
if [ -f "/tmp/playwright-mcp.pid" ]; then
    PID=$(cat /tmp/playwright-mcp.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo -e "${GREEN} Playwright MCP 服务已停止 (PID: $PID)${NC}"
    else
        echo -e "${YELLOW} Playwright MCP 服务未运行${NC}"
    fi
    rm -f /tmp/playwright-mcp.pid
else
    # 尝试通过端口查找
    PID=$(lsof -ti:3000)
    if [ ! -z "$PID" ]; then
        kill $PID
        echo -e "${GREEN} Playwright MCP 服务已停止 (PID: $PID)${NC}"
    else
        echo -e "${YELLOW} Playwright MCP 服务未运行${NC}"
    fi
fi

echo ""
echo -e "${YELLOW}[2/2] 停止 N-Tester MCP 服务...${NC}"

# 检查 PID 文件
if [ -f "/tmp/ntester-mcp.pid" ]; then
    PID=$(cat /tmp/ntester-mcp.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo -e "${GREEN} N-Tester MCP 服务已停止 (PID: $PID)${NC}"
    else
        echo -e "${YELLOW} N-Tester MCP 服务未运行${NC}"
    fi
    rm -f /tmp/ntester-mcp.pid
else
    # 尝试通过端口查找
    PID=$(lsof -ti:8006)
    if [ ! -z "$PID" ]; then
        kill $PID
        echo -e "${GREEN} N-Tester MCP 服务已停止 (PID: $PID)${NC}"
    else
        echo -e "${YELLOW} N-Tester MCP 服务未运行${NC}"
    fi
fi

echo ""
echo "========================================"
echo -e "  ${GREEN}所有服务已停止${NC}"
echo "========================================"
echo ""
