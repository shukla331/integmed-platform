@echo off
REM IntegMed Frontend Setup Script (Windows)
REM This script sets up Node.js dependencies and starts the dev server

echo.
echo ========================================
echo IntegMed Frontend Local Setup
echo ========================================
echo.

REM Check Node.js installation
echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)
echo OK: Node.js found

REM Check npm installation
echo Checking npm installation...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm is not installed
    pause
    exit /b 1
)
echo OK: npm found

echo.
echo Installing dependencies from package.json...
npm install

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the frontend dev server, run:
echo   npm run dev
echo.
echo Frontend will be available at:
echo   http://localhost:3000
echo.

pause
