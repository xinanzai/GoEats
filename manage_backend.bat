@echo off
chcp 65001 >nul
echo ========================================
echo 后台服务管理脚本
echo ========================================
echo.
echo 请选择操作:
echo 1 - 启动后端服务
echo 2 - 停止后端服务
echo 3 - 重启后端服务
echo 4 - 运行商家联调测试
echo 5 - 清理测试数据
echo.

set /p choice=请输入选项 (1-5): 

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto test
if "%choice%"=="5" goto cleanup

echo 无效选项！
goto end

:start
echo.
echo 正在启动后端服务...
start "Backend Server" cmd /k "cd /d "%~dp0backend" && ..\venv\Scripts\python.exe server.py"
echo 后端服务已启动在 http://localhost:8000
goto end

:stop
echo.
echo 正在停止后端服务...
taskkill /F /FI "WINDOWTITLE eq Backend Server*" /T >nul 2>&1
if %errorlevel% equ 0 (
    echo 后端服务已停止
) else (
    echo 未运行中的后端服务
)
goto end

:restart
call :stop
timeout /t 2 /nobreak >nul
call :start
goto end

:test
echo.
echo 正在运行商家联调测试...
cd /d "%~dp0"
venv\Scripts\python.exe test_merchant_integration.py
goto end

:cleanup
echo.
echo 正在清理测试数据...
cd /d "%~dp0"
venv\Scripts\python.exe -c "
import asyncio
import sys
sys.path.insert(0, 'backend')
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text

async def cleanup():
    engine = create_async_engine('sqlite+aiosqlite:///./backend/food_delivery.db')
    try:
        async with AsyncSession(engine) as session:
            await session.execute(text(\"DELETE FROM merchants WHERE user_id IN (SELECT id FROM users WHERE username='integration_test_merchant')\"))
            await session.execute(text(\"DELETE FROM users WHERE username='integration_test_merchant'\"))
            await session.commit()
            print('测试数据已清理')
    finally:
        await engine.dispose()

asyncio.run(cleanup())
"
goto end

:end
echo.
echo 操作完成！
pause
