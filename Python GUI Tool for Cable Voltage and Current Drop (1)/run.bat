@echo off

:: Check for Python installation
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3.10+ from python.org.
    pause
    exit /b 1
)

:: Check for pip installation
pip --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo pip is not installed. Please ensure pip is installed with your Python installation.
    pause
    exit /b 1
)

echo Checking and installing dependencies...

:: Install Pillow for image handling
pip install Pillow

echo Dependencies checked/installed. Launching GUI...

python cable_calculator.py

pause


