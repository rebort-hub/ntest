@echo off
echo 🚀 开始部署 Playwright Test Agents 完整服务

REM 1. 检查 PM2
where pm2 >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 📦 安装 PM2...
    npm install -g pm2
)

REM 2. 启动 Playwright MCP Server
echo 🎭 启动 Playwright MCP Server...
cd playwright-test-agents
pm2 start npx --name "playwright-mcp-1" -- playwright run-test-mcp-server --port 3001 --headless
pm2 start npx --name "playwright-mcp-2" -- playwright run-test-mcp-server --port 3002 --headless
pm2 start npx --name "playwright-mcp-3" -- playwright run-test-mcp-server --port 3003 --headless
cd ..

REM 3. 启动 N-Tester MCP（可选）
echo 🔧 启动 N-Tester MCP...
cd N-Tester_MCP
pm2 start python --name "n-tester-mcp" -- N-Tester_tools.py
cd ..

REM 4. 启动后端服务
echo 🐍 启动后端服务...
cd backend
pm2 start ".venv\Scripts\uvicorn.exe main:app --host 0.0.0.0 --port 8000" --name "backend"
cd ..

REM 5. 构建并启动前端服务
echo 🎨 构建前端服务...
cd frontend
call npm run build
pm2 start "npx serve -s dist -l 80" --name "frontend"
cd ..

REM 6. 保存 PM2 配置
pm2 save

echo ✅ 部署完成！
echo.
echo 📊 服务状态：
pm2 status
echo.
echo 🌐 访问地址：
echo   - 前端: http://localhost
echo   - 后端: http://localhost:8000
echo   - Playwright MCP 1: http://localhost:3001
echo   - Playwright MCP 2: http://localhost:3002
echo   - Playwright MCP 3: http://localhost:3003
echo   - N-Tester MCP: http://localhost:8006
echo.
echo 📝 查看日志：
echo   pm2 logs [服务名]
echo.
echo 🔄 重启服务：
echo   pm2 restart [服务名]

pause
