@echo off
echo ========================================
echo N-Tester MCP HTTP Wrapper
echo ========================================
echo.

echo 正在激活虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo 正在启动 HTTP API 服务...
echo 端口: 8080
echo 文档: http://127.0.0.1:8080/docs
echo.

python http_wrapper.py

pause
