@echo off
chcp 65001 >nul
echo ================================
echo   Python 依赖安装工具
echo ================================

cd /d "%~dp0"

REM 激活虚拟环境
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo [错误] 虚拟环境不存在，请先运行 deploy.bat
    pause
    exit /b 1
)

echo.
echo 请选择安装方式:
echo   1. 默认源（官方 PyPI）
echo   2. 清华镜像源（推荐国内用户）
echo   3. 阿里云镜像源
echo   4. 腾讯云镜像源
echo   5. 仅安装核心依赖（最小化安装）
echo.
set /p choice="请输入选项 (1-5): "

if "%choice%"=="1" (
    echo.
    echo 使用默认源安装...
    pip install -r requirements.txt
) else if "%choice%"=="2" (
    echo.
    echo 使用清华镜像源安装...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
) else if "%choice%"=="3" (
    echo.
    echo 使用阿里云镜像源安装...
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
) else if "%choice%"=="4" (
    echo.
    echo 使用腾讯云镜像源安装...
    pip install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple
) else if "%choice%"=="5" (
    echo.
    echo 安装核心依赖...
    pip install fastapi uvicorn tortoise-orm aerich python-dotenv
    pip install asyncpg aiomysql
    pip install pydantic loguru
    echo.
    echo [提示] 核心依赖已安装，其他依赖可按需安装
) else (
    echo [错误] 无效选项
    pause
    exit /b 1
)

if %errorlevel% neq 0 (
    echo.
    echo ================================
    echo   安装失败！
    echo ================================
    echo.
    echo 常见问题解决方案:
    echo.
    echo 1. 网络问题:
    echo    - 尝试使用镜像源（选项 2-4）
    echo    - 检查网络连接和代理设置
    echo.
    echo 2. 编译错误:
    echo    - 安装 Microsoft C++ Build Tools
    echo    - 下载地址: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo.
    echo 3. 权限问题:
    echo    - 以管理员身份运行
    echo.
    echo 4. 版本冲突:
    echo    - 检查 Python 版本: python --version
    echo    - 需要 Python 3.11+
    echo.
    pause
    exit /b 1
)

echo.
echo ================================
echo   安装成功！
echo ================================
echo.
echo 验证安装:
python -c "import fastapi; import tortoise; print('核心依赖正常')"
echo.
pause
