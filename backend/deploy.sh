#!/bin/bash

echo "================================"
echo "  N-Tester 测试平台一键部署"
echo "================================"

# 确保在 backend 目录
cd "$(dirname "$0")"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python 环境
echo ""
echo "[1/6] 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[错误] Python 3 未安装${NC}"
    echo "请先安装 Python 3.11+"
    exit 1
fi
python3 --version
echo -e "${GREEN}[成功] Python 环境检查通过${NC}"

# 检查虚拟环境
echo ""
echo "[2/6] 检查虚拟环境..."
if [ ! -d ".venv" ]; then
    echo "虚拟环境不存在，正在创建..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误] 虚拟环境创建失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}[成功] 虚拟环境创建完成${NC}"
else
    echo -e "${GREEN}[成功] 虚拟环境已存在${NC}"
fi

# 激活虚拟环境并安装依赖
echo ""
echo "[3/6] 安装 Python 依赖..."
source .venv/bin/activate
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}[警告] 部分依赖安装失败${NC}"
    echo ""
    echo "可能的原因:"
    echo "  1. 网络问题 - 尝试使用国内镜像源"
    echo "  2. 编译依赖缺失 - 某些包需要编译工具"
    echo "  3. 版本冲突 - 检查 Python 版本是否为 3.11+"
    echo ""
    echo "解决方案:"
    echo "  1. 使用依赖安装工具（推荐）: ./install_deps.sh"
    echo "  2. 跳过失败的包，继续部署"
    echo "  3. 退出并手动解决"
    echo ""
    read -p "请选择 (1/2/3): " continue_choice
    case $continue_choice in
        1)
            echo ""
            echo "启动依赖安装工具..."
            chmod +x install_deps.sh
            ./install_deps.sh
            if [ $? -ne 0 ]; then
                echo -e "${RED}[错误] 依赖安装仍然失败${NC}"
                exit 1
            fi
            ;;
        2)
            echo -e "${YELLOW}[继续] 跳过依赖安装错误，继续部署...${NC}"
            ;;
        *)
            echo -e "${RED}[退出] 部署已取消${NC}"
            exit 1
            ;;
    esac
else
    echo -e "${GREEN}[成功] 依赖安装完成${NC}"
fi

# 检查 .env 文件
echo ""
echo "[4/6] 检查配置文件..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}[警告] .env 文件不存在${NC}"
    if [ -f ".env.example" ]; then
        echo "正在从 .env.example 复制..."
        cp .env.example .env
        echo -e "${YELLOW}[提示] 请编辑 .env 文件配置数据库连接信息${NC}"
        read -p "按回车继续..."
    else
        echo -e "${RED}[错误] .env.example 文件也不存在${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}[成功] 配置文件已存在${NC}"
fi

# 初始化数据库
echo ""
echo "[5/6] 初始化数据库..."
echo "请选择操作:"
echo "  1. 首次部署（初始化数据库）"
echo "  2. 已有数据库（跳过初始化）"
echo "  3. 仅检查数据库状态"
read -p "请输入选项 (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "正在初始化数据库..."
        python -m aerich init -t app.configs.config.tortoise_orm_conf
        python -m aerich init-db
        python init_database.py --data
        if [ $? -ne 0 ]; then
            echo -e "${RED}[错误] 数据库初始化失败${NC}"
            exit 1
        fi
        echo -e "${GREEN}[成功] 数据库初始化完成${NC}"
        ;;
    2)
        echo -e "${YELLOW}[跳过] 数据库初始化${NC}"
        echo "正在应用迁移..."
        python -m aerich upgrade
        ;;
    3)
        echo ""
        python db_manager.py status
        exit 0
        ;;
    *)
        echo -e "${RED}[错误] 无效选项${NC}"
        exit 1
        ;;
esac

# 检查数据库状态
echo ""
echo "[6/6] 验证部署..."
python db_manager.py status
if [ $? -ne 0 ]; then
    echo -e "${RED}[错误] 数据库连接失败${NC}"
    exit 1
fi

echo ""
echo "================================"
echo "  部署完成！"
echo "================================"
echo ""
echo "默认账号:"
echo "  管理员: admin / 123456"
echo "  测试员: tester / tester"
echo "  负责人: manager / manager"
echo ""
echo "启动服务:"
echo "  开发模式: python main.py"
echo "  生产模式: ./start.sh"
echo ""
echo "定时任务:"
echo "  python scheduledtask/job.py"
echo ""
echo "其他命令:"
echo "  检查状态: python db_manager.py status"
echo "  生成迁移: python -m aerich migrate --name 描述"
echo "  应用迁移: python -m aerich upgrade"
echo ""
