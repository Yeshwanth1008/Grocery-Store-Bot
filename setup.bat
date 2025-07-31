@echo off
echo ========================================
echo    Grocery Store Bot Setup Script
echo ========================================
echo.

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)
python --version

echo.
echo [2/5] Installing required packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo [3/5] Setting up environment file...
if not exist .env (
    copy .env.template .env
    echo Environment file created from template
    echo Please edit .env file with your actual configuration
) else (
    echo Environment file already exists
)

echo.
echo [4/5] Database setup instructions...
echo Please ensure MySQL is installed and running
echo Then run the following commands in MySQL:
echo.
echo   CREATE DATABASE grocery_store;
echo   USE grocery_store;
echo   SOURCE database_schema.sql;
echo.

echo [5/5] Setup completed!
echo.
echo Next steps:
echo 1. Edit .env file with your bot token and database credentials
echo 2. Set up MySQL database using database_schema.sql
echo 3. Run: python Bot.py
echo.
echo For admin functions, run: python admin.py
echo.
pause
