@echo off
chcp 65001 >nul
echo ========================================
echo   Food Delivery System - Start Servers
echo ========================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [Error] Virtual environment not found
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo [1/4] Starting backend (port 8000)...
start "Backend" /d "%~dp0backend" cmd /k "..\venv\Scripts\python.exe server.py"
timeout /t 2 >nul

echo [2/4] Starting admin panel (port 5173)...
start "Admin" /d "%~dp0frontend\admin" cmd /k "npm run dev"
timeout /t 1 >nul

echo [3/4] Starting merchant panel (port 5174)...
start "Merchant" /d "%~dp0frontend\merchant" cmd /k "npm run dev"
timeout /t 1 >nul

echo [4/4] Starting user panel (port 5175)...
start "User" /d "%~dp0frontend\user" cmd /k "npm run dev"

echo.
echo ========================================
echo   All services started
echo ========================================
echo   Backend:        http://localhost:8000
echo   Admin Panel:    http://localhost:5173
echo   Merchant Panel: http://localhost:5174
echo   User Panel:     http://localhost:5175
echo.
echo   Run stop_server.bat to stop
echo ========================================
pause
