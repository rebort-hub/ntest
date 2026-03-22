@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   N-Tester MCP 增强版启动脚本
echo   集成官方 Playwright MCP
echo ========================================
echo.

REM 获取脚本所在目录的父目录的父目录（N-Tester_MCP 根目录）
set "ROOT_DIR=%~dp0..\.."
cd /d "%ROOT_DIR%"

echo [步骤 1/3] 检查环境...
echo.

REM 检查 Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo    错误: 未找到 Node.js
    echo    请先安装 Node.js: https://nodejs.org/
    pause
    exit /b 1
)

REM 检查 Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo    错误: 未找到 Python
    echo    请先安装 Python 3.8+
    pause
    exit /b 1
)

echo 环境检查通过
echo.

echo [步骤 2/3] 启动 Playwright MCP HTTP 桥接服务...
echo.

REM 检查桥接脚本是否存在
if not exist "src\integrations\playwright\http_bridge.js" (
    echo 错误: 未找到 src\integrations\playwright\http_bridge.js
    pause
    exit /b 1
)

REM 启动 Playwright MCP 桥接服务（新窗口）
start "Playwright MCP Bridge" cmd /k "node src\integrations\playwright\http_bridge.js"

echo    Playwright MCP 桥接服务已在新窗口启动
echo    监听地址: http://127.0.0.1:3000
echo.

REM 等待服务启动
echo 等待 Playwright MCP 服务启动...
timeout /t 5 /nobreak >nul

echo [步骤 3/3] 启动 N-Tester MCP 服务...
echo.

REM 检查 N-Tester MCP 主文件
if not exist "src\core\N-Tester_tools.py" (
    echo 错误: 未找到 src\core\N-Tester_tools.py
    pause
    exit /b 1
)

REM 检查 .env 文件
if not exist "config\.env" (
    echo    警告: 未找到 config\.env 文件
    echo    将使用默认配置
)

REM 设置环境变量
set PYTHONPATH=%CD%\src\core;%CD%\src\integrations\playwright;%PYTHONPATH%

REM 启动 N-Tester MCP 服务（新窗口）- 直接运行 N-Tester_tools.py
start "N-Tester MCP" cmd /k "cd /d %CD% && python src\core\N-Tester_tools.py"

echo    N-Tester MCP 服务已在新窗口启动
echo    监听地址: http://127.0.0.1:8006
echo.

echo ========================================
echo    所有服务已启动！
echo ========================================
echo.
echo    Playwright MCP: http://127.0.0.1:3000
echo    N-Tester MCP:   http://127.0.0.1:8006
echo.
echo   提示:
echo    - 两个服务窗口会保持打开状态
echo    - 关闭窗口即可停止对应服务
echo    - 查看窗口输出了解服务运行状态
echo.
echo 按任意键退出此窗口...
pause >nul
