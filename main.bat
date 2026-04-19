@echo off
title Inventory App Runner

echo [1/3] Checking Python...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b
)

echo [2/3] Installing requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install requirements.
    pause
    exit /b
)

echo [3/3] Running project...
python main.py

echo.
echo Done.
pause