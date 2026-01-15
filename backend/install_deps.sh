#!/bin/bash

echo "================================"
echo "  Python 依赖安装工具"
echo "================================"

cd "$(dirname "$0")"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 激活虚拟环境
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo -e "${RED}[错误] 虚拟环境不存在，请先运行 deploy.sh${NC}"
    exit 1
fi

echo ""
echo "请选择安装方式:"
echo "  1. 默认源（官方 PyPI）"
echo "  2. 清华镜像源（推荐国内用户）"
echo "  3. 阿里云镜像源"
echo "  4. 腾讯云镜像源"
echo "  5. 仅安装核心依赖（最小化安装）"
echo ""
read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "使用默认源安装..."
        pip install -r requirements.txt
        ;;
    2)
        echo ""
        echo "使用清华镜像源安装..."
        pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
        ;;
    3)
        echo ""
        echo "使用阿里云镜像源安装..."
        pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
        ;;
    4)
        echo ""
        echo "使用腾讯云镜像源安装..."
        pip install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple
        ;;
    5)
        echo ""
        echo "安装核心依赖..."
        pip install fastapi uvicorn tortoise-orm aerich python-dotenv
        pip install asyncpg aiomysql
        pip install pydantic loguru
        echo ""
        echo -e "${YELLOW}[提示] 核心依赖已安装，其他依赖可按需安装${NC}"
        ;;
    *)
        echo -e "${RED}[错误] 无效选项${NC}"
        exit 1
        ;;
esac

if [ $? -ne 0 ]; then
    echo ""
    echo "================================"
    echo "  安装失败！"
    echo "================================"
    echo ""
    echo "常见问题解决方案:"
    echo ""
    echo "1. 网络问题:"
    echo "   - 尝试使用镜像源（选项 2-4）"
    echo "   - 检查网络连接和代理设置"
    echo ""
    echo "2. 编译错误:"
    echo "   - 安装编译工具: sudo apt-get install build-essential python3-dev"
    echo "   - macOS: xcode-select --install"
    echo ""
    echo "3. 权限问题:"
    echo "   - 使用 sudo 或检查目录权限"
    echo ""
    echo "4. 版本冲突:"
    echo "   - 检查 Python 版本: python3 --version"
    echo "   - 需要 Python 3.11+"
    echo ""
    exit 1
fi

echo ""
echo "================================"
echo "  安装成功！"
echo "================================"
echo ""
echo "验证安装:"
python -c "import fastapi; import tortoise; print('核心依赖正常')"
echo ""
