@echo off
title LAN Chat Application Server (Listening on 0.0.0.0:5000)
color 0A
echo ======================================================================
echo          STARTING LAN CHAT APPLICATION SERVER
echo               Computer Networks College Project
echo ======================================================================
echo.

:: Activate virtual environment if present
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment 'venv'...
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found, running using global Python...
)

echo Starting Flask-SocketIO Server on 0.0.0.0:5000...
echo.

cd backend
python app.py

echo.
echo Server stopped.
pause
