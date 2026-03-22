@echo off
chcp 65001 >nul
echo ========================================
echo   停止 N-Tester MCP 服务
echo ========================================
echo.

echo [1/2] 停止 Playwright MCP 桥接服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    echo 找到进程 PID: %%a
    taskkill /PID %%a /F >nul 2>&1
    if !errorlevel! equ 0 (
        echo Playwright MCP 服务已停止
    )
)

echo.
echo [2/2] 停止 N-Tester MCP 服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8006') do (
    echo 找到进程 PID: %%a
    taskkill /PID %%a /F >nul 2>&1
    if !errorlevel! equ 0 (
        echo  N-Tester MCP 服务已停止
    )
)

echo.
echo ========================================
echo   所有服务已停止
echo ========================================
echo.
pause
