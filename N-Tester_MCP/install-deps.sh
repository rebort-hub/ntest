#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "  安装 N-Tester MCP 依赖"
echo "========================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}[1/2] 安装 Node.js 依赖...${NC}"
if [ -f "package.json" ]; then
    npm install
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Node.js 依赖安装完成${NC}"
    else
        echo -e "${RED}❌ Node.js 依赖安装失败${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️ 未找到 package.json，跳过 Node.js 依赖安装${NC}"
fi

echo ""
echo -e "${BLUE}[2/2] 安装 Python 依赖...${NC}"

# 使用 python3 或 python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

if [ -f "requirements.txt" ]; then
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Python 依赖安装完成${NC}"
    else
        echo -e "${RED}❌ Python 依赖安装失败${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️ 未找到 requirements.txt，跳过 Python 依赖安装${NC}"
fi

echo ""
echo "========================================"
echo -e "  ${GREEN}依赖安装完成！${NC}"
echo "========================================"
echo ""
echo "💡 下一步: 运行 ./start.sh 启动服务"
echo ""
