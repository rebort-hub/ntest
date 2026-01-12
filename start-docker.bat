@echo off
echo ================================
echo   N-Tester测试平台 Docker 一键部署
echo ================================

echo.
echo 检查 Docker 环境...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Docker 未安装或未启动
    echo 请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Docker Compose 未安装
    echo 请确保 Docker Desktop 包含 Docker Compose
    pause
    exit /b 1
)

echo [成功] Docker 环境检查通过

echo.
echo 启动服务...
docker-compose up -d

echo.
echo 等待服务启动...
timeout /t 10 /nobreak >nul

echo.
echo 检查服务状态...
docker-compose ps

echo.
echo ================================
echo   部署完成！
echo ================================
echo.
echo 访问地址:
echo   前端: http://localhost
echo   后端API: http://localhost:8018
echo   API文档: http://localhost:8018/docs
echo.
echo 管理命令:
echo   查看日志: docker-compose logs -f
echo   停止服务: docker-compose down
echo   重启服务: docker-compose restart
echo.
echo 按任意键退出...
pause >nul