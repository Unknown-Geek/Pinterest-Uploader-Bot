@echo off
echo Pinterest Auto-Publisher Startup
echo ===============================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Installing/checking dependencies...
pip install -r requirements.txt

REM Start the application directly
echo.
echo Starting Pinterest Auto-Publisher...
echo Open your browser and go to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

pause
