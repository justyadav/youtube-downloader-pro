@echo off
title YouTube Downloader Pro - Web Server
cd /d "%~dp0"

echo ========================================================
echo        Starting YouTube Downloader Pro (Web GUI)
echo ========================================================
echo.

IF NOT EXIST "venv\Scripts\python.exe" (
    echo Virtual environment not found. Setting up...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) ELSE (
    call venv\Scripts\activate.bat
)

echo Opening browser at http://localhost:8000 ...
python server.py

pause
