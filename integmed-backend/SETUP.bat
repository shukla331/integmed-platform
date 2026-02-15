@echo off
REM IntegMed Backend Setup Script (Windows)
REM This script sets up the Python environment and installs dependencies

echo.
echo ========================================
echo IntegMed Backend Local Setup
echo ========================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11.8 from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo OK: Python found

echo.
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    echo Virtual environment created
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies from requirements.txt...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Running database migrations...
REM Assuming database is already set up at localhost:5432
alembic upgrade head

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the backend API, run:
echo   venv\Scripts\activate.bat
echo   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
echo.
echo Backend will be available at:
echo   http://localhost:8000
echo   API Docs: http://localhost:8000/api/v1/docs
echo.

pause
