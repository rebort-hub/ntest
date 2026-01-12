#!/bin/bash

echo "================================"
echo "   N-Tester测试平台 Docker 一键部署"
echo "================================"

echo ""
echo "检查 Docker 环境..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "[错误] Docker 未安装"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "[错误] Docker Compose 未安装"
    echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "[成功] Docker 环境检查通过"

echo ""
echo "启动服务..."
docker-compose up -d

echo ""
echo "等待服务启动..."
sleep 10

echo ""
echo "检查服务状态..."
docker-compose ps

echo ""
echo "================================"
echo "   部署完成！"
echo "================================"
echo ""
echo "访问地址:"
echo "  前端: http://localhost"
echo "  后端API: http://localhost:8018"
echo "  API文档: http://localhost:8018/docs"
echo ""
echo "管理命令:"
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo ""