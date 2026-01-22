#!/bin/bash
echo "================================"
echo "  N-Tester 测试平台一键部署 (Linux)"
echo "================================"

# 初始化变量
PYTHON_CMD=python3
PIP_CMD=pip3
VENV_NAME=.venv
LOG_FILE=install.log
REQUIREMENTS=requirements.txt

cd "$(dirname "$0")"

# 清空旧日志
if [ -f "$LOG_FILE" ]; then
    rm -f "$LOG_FILE"
fi

# 1. 检查Python环境
echo
echo "[1/6] 检查 Python 环境..."
$PYTHON_CMD --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[错误] Python 未安装或未添加到 PATH" | tee -a "$LOG_FILE"
    echo "请先安装 Python 3.11+"
    exit 1
fi
$PYTHON_CMD --version
echo "[成功] Python 环境检查通过"

# 2. 检查/创建虚拟环境
echo
echo "[2/6] 检查虚拟环境..."
if [ ! -d "$VENV_NAME" ]; then
    echo "正在创建虚拟环境..."
    $PYTHON_CMD -m venv "$VENV_NAME"
    if [ $? -ne 0 ]; then
        echo "[错误] 虚拟环境创建失败" | tee -a "$LOG_FILE"
        exit 1
    fi
    echo "[成功] 虚拟环境创建完成"
else
    echo "[成功] 虚拟环境已存在"
fi

# 3. 安装依赖
echo
echo "[3/6] 安装 Python 依赖..."
source "$VENV_NAME/bin/activate"

# 检查pip版本
$PYTHON_CMD -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "[警告] pip更新失败，继续尝试安装依赖" >> "$LOG_FILE"
fi

# 安装依赖（带重试机制）
RETRY_COUNT=3
INSTALL_SUCCESS=0

for i in $(seq 1 $RETRY_COUNT); do
    echo "正在安装依赖(尝试次数: $i)..."
    $PYTHON_CMD -m pip install -r "$REQUIREMENTS" --quiet --progress-bar off >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        INSTALL_SUCCESS=1
        break
    else
        echo "安装失败，剩余重试次数: $((RETRY_COUNT - i))"
        sleep 5
    fi
done

if [ $INSTALL_SUCCESS -eq 0 ]; then
    echo
    echo "[警告] 部分依赖安装失败" | tee -a "$LOG_FILE"
    echo "详细日志请查看: $LOG_FILE"
    
    echo
    echo "可能的原因:"
    echo "  1. 网络问题 - 尝试使用国内镜像源"
    echo "  2. 编译依赖缺失 - 某些包需要C++编译器"
    echo "  3. 版本冲突 - 检查Python版本是否为3.11+"
    
    echo
    read -p "请选择操作 (1重试镜像源/2继续/3退出): " continue_choice
    case "$continue_choice" in
        1)
            echo "正在使用阿里云镜像源重试..."
            $PYTHON_CMD -m pip install -r "$REQUIREMENTS" -i https://mirrors.aliyun.com/pypi/simple/ >> "$LOG_FILE" 2>&1
            if [ $? -ne 0 ]; then
                echo "[错误] 镜像源安装仍然失败"
                exit 1
            fi
            echo "[成功] 依赖安装完成"
            ;;
        2)
            echo "[继续] 跳过依赖安装错误，继续部署..."
            ;;
        *)
            echo "[退出] 部署已取消"
            exit 1
            ;;
    esac
else
    echo "[成功] 依赖安装完成"
fi

# 4. 检查配置文件
echo
echo "[4/6] 检查配置文件..."
if [ ! -f ".env" ]; then
    echo "[警告] .env 文件不存在"
    if [ -f ".env.example" ]; then
        echo "正在从 .env.example 复制..."
        cp -f ".env.example" ".env"
        echo "[提示] 请编辑 .env 文件配置数据库连接信息"
    else
        echo "[错误] .env.example 文件也不存在" | tee -a "$LOG_FILE"
        exit 1
    fi
else
    echo "[成功] 配置文件已存在"
fi

# 5. 数据库初始化
echo
echo "[5/6] 数据库配置..."
echo "请选择操作:"
echo "  1. 首次部署（初始化数据库）"
echo "  2. 已有数据库（跳过初始化）"
echo "  3. 仅检查数据库状态"
read -p "请输入选项 (1/2/3): " db_choice

case "$db_choice" in
    1)
        echo
        echo "[步骤1/3] 初始化Aerich迁移配置..."
        $PYTHON_CMD -m aerich init -t app.configs.config.tortoise_orm_conf
        if [ $? -ne 0 ]; then
            echo "[错误] Aerich初始化失败" | tee -a "$LOG_FILE"
            exit 1
        fi
        
        echo "[步骤2/3] 初始化数据库表结构..."
        $PYTHON_CMD -m aerich init-db
        if [ $? -ne 0 ]; then
            echo "[错误] 数据库表初始化失败" | tee -a "$LOG_FILE"
            exit 1
        fi
        
        echo "[步骤3/3] 插入初始数据..."
        $PYTHON_CMD db_manager.py setup
        if [ $? -ne 0 ]; then
            echo "[错误] 初始数据插入失败" | tee -a "$LOG_FILE"
            exit 1
        fi
        
        echo "[成功] 数据库初始化完成"
        ;;
    2)
        echo "[跳过] 数据库初始化"
        echo "正在应用迁移..."
        $PYTHON_CMD -m aerich upgrade
        ;;
    3)
        echo
        $PYTHON_CMD db_manager.py status
        exit 0
        ;;
    *)
        echo "[错误] 无效选项"
        exit 1
        ;;
esac

# 6. 验证部署
echo
echo "[6/6] 验证部署..."
$PYTHON_CMD db_manager.py status
if [ $? -ne 0 ]; then
    echo "[错误] 数据库连接失败" | tee -a "$LOG_FILE"
    exit 1
fi

# 完成提示
echo
echo "================================"
echo "  N-tester平台部署完成！"
echo "================================"
echo
echo "默认账号:"
echo "  管理员: admin / 123456"
echo "  测试员: tester / tester"
echo "  负责人: manager / manager"
echo
echo "启动服务:"
echo "  开发模式: $PYTHON_CMD main.py"
echo "  生产模式: $PYTHON_CMD -m gunicorn -c gunicorn_main.py main:app"
echo
echo "定时任务:"
echo "  $PYTHON_CMD scheduledtask/job.py"
echo "  或: $PYTHON_CMD -m gunicorn -c gunicorn_job.py scheduledtask.job:job"
echo
echo "其他命令:"
echo "  检查状态: $PYTHON_CMD db_manager.py status"
echo "  生成迁移: $PYTHON_CMD -m aerich migrate --name 描述"
echo "  应用迁移: $PYTHON_CMD -m aerich upgrade"
echo
echo "详细安装日志: $LOG_FILE"