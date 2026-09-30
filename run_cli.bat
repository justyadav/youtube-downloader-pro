@echo off
title YouTube Downloader Pro - CLI
cd /d "%~dp0"

IF NOT EXIST "venv\Scripts\python.exe" (
    echo Virtual environment not found. Setting up...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) ELSE (
    call venv\Scripts\activate.bat
)

python downloader_cli.py

pause
