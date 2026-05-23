@echo off
chcp 65001 >nul
echo Starting backend server on port 8000...
cd /d "%~dp0"
..\venv\Scripts\python.exe server.py
