@echo off
chcp 65001 >nul
echo ========================================
echo   测试新目录结构
echo ========================================
echo.

cd /d "%~dp0"

echo [1/5] 检查核心文件...
if exist "src\core\N-Tester_tools.py" (
    echo ✅ src\core\N-Tester_tools.py
) else (
    echo ❌ 缺少 src\core\N-Tester_tools.py
)

if exist "src\core\ms_mcp_api.py" (
    echo ✅ src\core\ms_mcp_api.py
) else (
    echo ❌ 缺少 src\core\ms_mcp_api.py
)

if exist "src\core\config_enhanced.py" (
    echo ✅ src\core\config_enhanced.py
) else (
    echo ❌ 缺少 src\core\config_enhanced.py
)

echo.
echo [2/5] 检查 Playwright 集成...
if exist "src\integrations\playwright\http_bridge.js" (
    echo ✅ src\integrations\playwright\http_bridge.js
) else (
    echo ❌ 缺少 src\integrations\playwright\http_bridge.js
)

if exist "src\integrations\playwright\enhanced_playwright_integration.py" (
    echo ✅ src\integrations\playwright\enhanced_playwright_integration.py
) else (
    echo ❌ 缺少 src\integrations\playwright\enhanced_playwright_integration.py
)

if exist "src\integrations\playwright\config.json" (
    echo ✅ src\integrations\playwright\config.json
) else (
    echo ❌ 缺少 src\integrations\playwright\config.json
)

echo.
echo [3/5] 检查包装器...
if exist "src\wrappers\http_wrapper.py" (
    echo ✅ src\wrappers\http_wrapper.py
) else (
    echo ❌ 缺少 src\wrappers\http_wrapper.py
)

if exist "src\wrappers\start_http_wrapper.py" (
    echo ✅ src\wrappers\start_http_wrapper.py
) else (
    echo ❌ 缺少 src\wrappers\start_http_wrapper.py
)

echo.
echo [4/5] 检查启动脚本...
if exist "scripts\start\start-enhanced.bat" (
    echo ✅ scripts\start\start-enhanced.bat
) else (
    echo ❌ 缺少 scripts\start\start-enhanced.bat
)

if exist "start.bat" (
    echo ✅ start.bat
) else (
    echo ❌ 缺少 start.bat
)

echo.
echo [5/5] 检查测试脚本...
if exist "scripts\test\test_bridge_service.js" (
    echo ✅ scripts\test\test_bridge_service.js
) else (
    echo ❌ 缺少 scripts\test\test_bridge_service.js
)

if exist "scripts\test\test_list_playwright_tools.py" (
    echo ✅ scripts\test\test_list_playwright_tools.py
) else (
    echo ❌ 缺少 scripts\test\test_list_playwright_tools.py
)

echo.
echo ========================================
echo   测试完成！
echo ========================================
echo.
echo 💡 下一步:
echo    1. 运行 start.bat 启动服务
echo    2. 查看 MIGRATION_COMPLETE.md 了解详情
echo.
pause
