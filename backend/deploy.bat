@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================
echo   N-Tester 测试平台一键部署
echo ================================

:: 初始化变量
set PYTHON_CMD=python
set PIP_CMD=pip
set VENV_NAME=.venv
set LOG_FILE=install.log
set REQUIREMENTS=requirements.txt

cd /d "%~dp0"

:: 清空旧日志
if exist %LOG_FILE% del %LOG_FILE%

:: 1. 检查Python环境
echo.
echo [1/6] 检查 Python 环境...
%PYTHON_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Python 未安装或未添加到 PATH >> %LOG_FILE%
    echo [错误] Python 未安装或未添加到 PATH
    echo 请先安装 Python 3.11+
    pause
    exit /b 1
)
%PYTHON_CMD% --version
echo [成功] Python 环境检查通过

:: 2. 检查/创建虚拟环境
echo.
echo [2/6] 检查虚拟环境...
if not exist %VENV_NAME% (
    echo 正在创建虚拟环境...
    %PYTHON_CMD% -m venv %VENV_NAME%
    if %errorlevel% neq 0 (
        echo [错误] 虚拟环境创建失败 >> %LOG_FILE%
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo [成功] 虚拟环境创建完成
) else (
    echo [成功] 虚拟环境已存在
)

:: 3. 安装依赖
echo.
echo [3/6] 安装 Python 依赖...
call %VENV_NAME%\Scripts\activate.bat

:: 检查pip版本
%PYTHON_CMD% -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [警告] pip更新失败，继续尝试安装依赖 >> %LOG_FILE%
)

:: 安装依赖（带重试机制）
set RETRY_COUNT=3
set INSTALL_SUCCESS=0

:INSTALL_DEPS
echo 正在安装依赖(尝试次数: !RETRY_COUNT!)...
%PYTHON_CMD% -m pip install -r %REQUIREMENTS% --quiet --progress-bar off >> %LOG_FILE% 2>&1
if %errorlevel% equ 0 (
    set INSTALL_SUCCESS=1
    goto :DEPS_INSTALLED
) else (
    set /a RETRY_COUNT-=1
    if !RETRY_COUNT! gtr 0 (
        echo 安装失败，剩余重试次数: !RETRY_COUNT!
        timeout /t 5 >nul
        goto :INSTALL_DEPS
    )
)

:DEPS_INSTALLED
if %INSTALL_SUCCESS% equ 0 (
    echo.
    echo [警告] 部分依赖安装失败 >> %LOG_FILE%
    echo [警告] 部分依赖安装失败
    echo 详细日志请查看: %LOG_FILE%
    
    echo.
    echo 可能的原因:
    echo   1. 网络问题 - 尝试使用国内镜像源
    echo   2. 编译依赖缺失 - 某些包需要C++编译器
    echo   3. 版本冲突 - 检查Python版本是否为3.11+
    
    echo.
    set /p continue_choice="请选择操作 (1重试镜像源/2继续/3退出): "
    if "!continue_choice!"=="1" (
        echo 正在使用阿里云镜像源重试...
        %PYTHON_CMD% -m pip install -r %REQUIREMENTS% -i https://mirrors.aliyun.com/pypi/simple/ >> %LOG_FILE% 2>&1
        if %errorlevel% neq 0 (
            echo [错误] 镜像源安装仍然失败
            pause
            exit /b 1
        )
        echo [成功] 依赖安装完成
    ) else if "!continue_choice!"=="2" (
        echo [继续] 跳过依赖安装错误，继续部署...
    ) else (
        echo [退出] 部署已取消
        pause
        exit /b 1
    )
) else (
    echo [成功] 依赖安装完成
)

:: 4. 检查配置文件
echo.
echo [4/6] 检查配置文件...
if not exist .env (
    echo [警告] .env 文件不存在
    if exist .env.example (
        echo 正在从 .env.example 复制...
        copy /y .env.example .env >nul
        echo [提示] 请编辑 .env 文件配置数据库连接信息
        pause
    ) else (
        echo [错误] .env.example 文件也不存在 >> %LOG_FILE%
        echo [错误] .env.example 文件也不存在
        pause
        exit /b 1
    )
) else (
    echo [成功] 配置文件已存在
)

:: 5. 数据库初始化
echo.
echo [5/6] 数据库配置...
echo 请选择操作:
echo   1. 首次部署（初始化数据库）
echo   2. 已有数据库（跳过初始化）
echo   3. 仅检查数据库状态
set /p db_choice="请输入选项 (1/2/3): "

if "!db_choice!"=="1" (
    echo.
    echo [步骤1/3] 初始化Aerich迁移配置...
    %PYTHON_CMD% -m aerich init -t app.configs.config.tortoise_orm_conf
    if %errorlevel% neq 0 (
        echo [错误] Aerich初始化失败 >> %LOG_FILE%
        echo [错误] Aerich初始化失败
        pause
        exit /b 1
    )
    
    echo [步骤2/3] 初始化数据库表结构...
    %PYTHON_CMD% -m aerich init-db
    if %errorlevel% neq 0 (
        echo [错误] 数据库表初始化失败 >> %LOG_FILE%
        echo [错误] 数据库表初始化失败
        pause
        exit /b 1
    )
    
    echo [步骤3/3] 插入初始数据...
    %PYTHON_CMD% db_manager.py setup
    if %errorlevel% neq 0 (
        echo [错误] 初始数据插入失败 >> %LOG_FILE%
        echo [错误] 初始数据插入失败
        pause
        exit /b 1
    )
    
    echo [成功] 数据库初始化完成
) else if "!db_choice!"=="2" (
    echo [跳过] 数据库初始化
    echo 正在应用迁移...
    %PYTHON_CMD% -m aerich upgrade
) else if "!db_choice!"=="3" (
    echo.
    %PYTHON_CMD% db_manager.py status
    pause
    exit /b 0
) else (
    echo [错误] 无效选项
    pause
    exit /b 1
)

:: 6. 验证部署
echo.
echo [6/6] 验证部署...
%PYTHON_CMD% db_manager.py status
if %errorlevel% neq 0 (
    echo [错误] 数据库连接失败 >> %LOG_FILE%
    echo [错误] 数据库连接失败
    pause
    exit /b 1
)

:: 完成提示
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
echo   开发模式: %PYTHON_CMD% main.py
echo   生产模式: %PYTHON_CMD% -m gunicorn -c gunicorn_main.py main:app
echo.
echo 定时任务:
echo   %PYTHON_CMD% scheduledtask/job.py
echo   或: %PYTHON_CMD% -m gunicorn -c gunicorn_job.py scheduledtask.job:job
echo.
echo 其他命令:
echo   检查状态: %PYTHON_CMD% db_manager.py status
echo   生成迁移: %PYTHON_CMD% -m aerich migrate --name 描述
echo   应用迁移: %PYTHON_CMD% -m aerich upgrade
echo.
echo 详细安装日志: %LOG_FILE%
pause