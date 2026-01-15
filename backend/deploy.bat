@echo off
chcp 65001 >nul
echo ================================
echo   N-Tester 测试平台一键部署
echo ================================

cd /d "%~dp0"

REM 检查 Python 环境是否存在
echo.
echo [1/6] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Python 未安装或未添加到 PATH
    echo 请先安装 Python 3.11+
    pause
    exit /b 1
)
python --version
echo [成功] Python 环境检查通过

REM 检查虚拟环境
echo.
echo [2/6] 检查虚拟环境有没有...
if not exist .venv (
    echo 没看到有任何虚拟环境创建，我创建一个...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo [成功] 虚拟环境创建完成
) else (
    echo [成功] 虚拟环境已存在，无须重复创建
)

REM 激活虚拟环境并安装依赖
echo.
echo [3/6] 安装 Python 依赖...
call .venv\Scripts\activate.bat
pip install -r requirements.txt
    echo.
    echo [警告] 部分依赖安装失败
    echo.
    echo 可能的原因:
    echo   1. 网络问题 - 尝试使用国内镜像源
    echo   2. 编译依赖缺失 - 某些包需要 C++ 编译器
    echo   3. 版本冲突 - 检查 Python 版本是否为 3.11+
    echo.
    echo 解决方案:
    echo   1. 使用依赖安装工具（推荐）: install_deps.bat
    echo   2. 跳过失败的包，继续部署
    echo   3. 退出并手动解决
    echo.
    set /p continue_choice="请选择 (1/2/3): "
    if "%continue_choice%"=="1" (
        echo.
        echo 启动依赖安装工具...
        call install_deps.bat
        if %errorlevel% neq 0 (
            echo [错误] 依赖安装仍然失败
            pause
            exit /b 1
        )
    ) else if "%continue_choice%"=="2" (
        echo [继续] 跳过依赖安装错误，继续部署...
    ) else (
        echo [退出] 部署已取消
        pause
        exit /b 1
    )
) else (
    echo [成功] 依赖安装完成
)

REM 检查 .env 文件
echo.
echo [4/6] 检查配置文件...
if not exist .env (
    echo [警告] .env 文件不存在
    if exist .env.example (
        echo 正在从 .env.example 复制...
        copy .env.example .env
        echo [提示] 请编辑 .env 文件配置数据库连接信息
        pause
    ) else (
        echo [错误] .env.example 文件也不存在
        pause
        exit /b 1
    )
) else (
    echo [成功] 配置文件已存在
)

REM 初始化数据库
echo.
echo [5/6] 初始化数据库...
echo 请选择操作:
echo   1. 首次部署（初始化数据库）
echo   2. 已有数据库（跳过初始化）
echo   3. 仅检查数据库状态
set /p choice="请输入选项 (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo 正在初始化数据库...
    python -m aerich init -t app.configs.config.tortoise_orm_conf
    python -m aerich init-db
    python init_database.py --data
    if %errorlevel% neq 0 (
        echo [错误] 数据库初始化失败
        pause
        exit /b 1
    )
    echo [成功] 数据库初始化完成
) else if "%choice%"=="2" (
    echo [跳过] 数据库初始化
    echo 正在应用迁移...
    python -m aerich upgrade
) else if "%choice%"=="3" (
    echo.
    python db_manager.py status
    pause
    exit /b 0
) else (
    echo [错误] 无效选项
    pause
    exit /b 1
)

REM 检查数据库状态
echo.
echo [6/6] 验证部署...
python db_manager.py status
if %errorlevel% neq 0 (
    echo [错误] 数据库连接失败
    pause
    exit /b 1
)

echo.
echo ================================
echo   N-tester平台部署完成！
echo ================================
echo.
echo 默认账号:
echo   管理员: admin / 123456
echo   测试员: tester / tester
echo   负责人: manager / manager
echo.
echo 启动服务:
echo   开发模式: python main.py
echo   生产模式: python -m gunicorn -c gunicorn_main.py main:app
echo.
echo 定时任务:
echo   python scheduledtask/job.py
echo   或: python -m gunicorn -c gunicorn_job.py scheduledtask.job:job
echo.
echo 其他命令:
echo   检查状态: python db_manager.py status
echo   生成迁移: python -m aerich migrate --name 描述
echo   应用迁移: python -m aerich upgrade
echo.
pause
