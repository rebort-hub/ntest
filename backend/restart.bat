@echo off
echo ========================================
echo 强制重启后端服务
echo ========================================
echo.

echo 正在停止所有 Python 进程...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo 正在激活虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo 正在启动后端服务...
python main.py

pause
