@echo off
title Inventory App Runner

echo [1/3] Checking Python...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b
)

echo [2/3] Checking dependencies...

python -m pip install --upgrade pip

python -c "import pkg_resources; pkg_resources.require(open('requirements.txt').read().splitlines())" >nul 2>&1

IF %ERRORLEVEL% EQU 0 (
    echo All dependencies already installed.
) ELSE (
    echo Installing missing dependencies...
    python -m pip install -r requirements.txt
    IF %ERRORLEVEL% NEQ 0 (
        echo Failed to install requirements.
        pause
        exit /b
    )
)

echo [3/3] Running Streamlit UI...

python -m streamlit run ui/app.py

echo.
echo Done.
pause