@echo off
title LAN Chat Application - Setup Environment
color 0B
echo ======================================================================
echo          LAN CHAT APPLICATION - ENVIRONMENT SETUP
echo               Computer Networks College Project
echo ======================================================================
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your system PATH!
    echo Please install Python 3.9+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [1/3] Python found:
python --version
echo.

:: Create Virtual Environment
if not exist "venv\" (
    echo [2/3] Creating Python virtual environment in .\venv ...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo [2/3] Virtual environment 'venv' already exists. Skipping creation.
)
echo.

:: Install Dependencies
echo [3/3] Installing required packages (Flask, Flask-SocketIO, SQLAlchemy)...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Dependency installation encountered an issue.
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo [SUCCESS] Setup is complete!
echo To start the server anytime, simply double-click "run_server.bat"
echo ======================================================================
echo.
pause
