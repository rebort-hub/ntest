@echo off
REM Windows批处理脚本 - 安装依赖并测试

echo ========================================
echo LLM对话功能集成 - 安装和测试
echo ========================================
echo.

REM 激活虚拟环境
echo [1/4] 激活虚拟环境...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo 使用 .venv 虚拟环境
) else if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo 使用 venv 虚拟环境
) else (
    echo 错误: 未找到虚拟环境！
    echo 请先创建虚拟环境: python -m venv .venv
    pause
    exit /b 1
)

echo.
echo [2/4] 安装新依赖...
pip install aiosqlite langgraph langchain-core langchain-openai
if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败！
    pause
    exit /b 1
)

echo.
echo [3/4] 运行快速测试...
python quick_test.py
if %errorlevel% neq 0 (
    echo 警告: 部分测试失败，请检查错误信息
) else (
    echo 所有测试通过！
)

echo.
echo [4/4] 测试完成！
echo.
echo 下一步:
echo 1. 执行数据库迁移: mysql -u user -p database ^< migrations/add_llm_config_fields.sql
echo 2. 启动后端服务: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
echo 3. 启动前端服务: cd ../test-platform-fastapi-front ^&^& npm run dev
echo.

pause
