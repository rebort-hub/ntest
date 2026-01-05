#!/bin/bash

# 前端部署脚本 - 解决缓存问题

echo "开始构建前端项目..."

# 清理之前的构建文件
rm -rf dist/

# 构建项目
npm run build

echo "构建完成，开始部署..."

# 如果使用Docker部署
if [ -f "Dockerfile" ]; then
    echo "使用Docker部署..."
    
    # 停止并删除旧容器
    docker stop frontend-container 2>/dev/null || true
    docker rm frontend-container 2>/dev/null || true
    
    # 删除旧镜像
    docker rmi frontend-image 2>/dev/null || true
    
    # 构建新镜像
    docker build -t frontend-image .
    
    # 运行新容器
    docker run -d --name frontend-container -p 80:80 frontend-image
    
    echo "Docker部署完成！"
else
    echo "请根据你的部署方式修改此脚本"
fi

echo "部署完成！建议用户清理浏览器缓存或使用Ctrl+F5强制刷新"