@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo ========================================
echo   外卖点餐系统 - 数据库初始化
echo ========================================
echo.

if exist "..\venv\Scripts\activate.bat" (
    call "..\venv\Scripts\activate.bat"
) else (
    echo [错误] 未找到虚拟环境，请先创建虚拟环境
    echo.
    echo 请运行: python -m venv venv
    echo.
    pause
    exit /b 1
)

python init_database.py

echo.
pause
