#!/bin/bash

echo "🚀 启动 N-Tester 测试平台"
echo "================================"

# 确保在 backend 目录
cd "$(dirname "$0")"

# 检查 Python 环境
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11 未找到"
    echo "请安装 Python 3.11 或修改脚本中的 Python 路径"
    exit 1
fi

# 启动主应用
echo "📝 启动主应用服务..."
nohup python3.11 -m gunicorn -c gunicorn_main.py main:app > logs/main.log 2>&1 &
MAIN_PID=$!
echo "✅ 主应用已启动 (PID: $MAIN_PID)"

# 启动定时任务服务
echo "📝 启动定时任务服务..."
nohup python3.11 -m gunicorn -c gunicorn_job.py scheduledtask.job:job > logs/job.log 2>&1 &
JOB_PID=$!
echo "✅ 定时任务已启动 (PID: $JOB_PID)"

# 保存 PID
echo $MAIN_PID > pids/main.pid
echo $JOB_PID > pids/job.pid

echo ""
echo "================================"
echo "✅ 所有服务启动完成！"
echo "================================"
echo ""
echo "访问地址:"
echo "  主应用: http://localhost:8018"
echo "  API文档: http://localhost:8018/docs"
echo "  定时任务: http://localhost:8019"
echo ""
echo "日志文件:"
echo "  主应用: logs/main.log"
echo "  定时任务: logs/job.log"
echo ""
echo "停止服务: ./kill.sh"
echo ""