@echo off
echo ========================================
echo 启动 FastAPI 后端服务
echo ========================================
echo.

REM 激活虚拟环境
call .venv\Scripts\activate.bat

echo 虚拟环境已激活
echo.
echo 启动服务...
echo 访问地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.

REM 启动uvicorn服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
