@echo off
chcp 65001 >nul
echo ========================================
echo   安装 N-Tester MCP 依赖
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] 安装 Node.js 依赖...
if exist "package.json" (
    call npm install
    if %errorlevel% equ 0 (
        echo ✅ Node.js 依赖安装完成
    ) else (
        echo ❌ Node.js 依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo ⚠️ 未找到 package.json，跳过 Node.js 依赖安装
)

echo.
echo [2/2] 安装 Python 依赖...
if exist "requirements.txt" (
    python -m pip install -r requirements.txt
    if %errorlevel% equ 0 (
        echo ✅ Python 依赖安装完成
    ) else (
        echo ❌ Python 依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo ⚠️ 未找到 requirements.txt，跳过 Python 依赖安装
)

echo.
echo ========================================
echo   依赖安装完成！
echo ========================================
echo.
echo 💡 下一步: 运行 start.bat 启动服务
echo.
pause
