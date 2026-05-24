@echo off
chcp 65001 >nul
echo ========================================
echo   Food Delivery System - Stop Servers
echo ========================================
echo.

echo [1/4] Stopping backend...
taskkill /FI "WINDOWTITLE eq Backend *" /T >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Backend stopped
) else (
    echo   [--] Backend not running
)

echo [2/4] Stopping admin panel...
taskkill /FI "WINDOWTITLE eq Admin *" /T >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Admin stopped
) else (
    echo   [--] Admin not running
)

echo [3/4] Stopping merchant panel...
taskkill /FI "WINDOWTITLE eq Merchant *" /T >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Merchant stopped
) else (
    echo   [--] Merchant not running
)

echo [4/4] Stopping user panel...
taskkill /FI "WINDOWTITLE eq User *" /T >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] User stopped
) else (
    echo   [--] User not running
)

echo.
echo ========================================
echo   All services stopped
echo ========================================
pause
