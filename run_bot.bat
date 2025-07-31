@echo off
echo ========================================
echo    Starting Grocery Store Bot
echo ========================================
echo.

echo Checking environment setup...
if not exist .env (
    echo ERROR: .env file not found!
    echo Please run setup.bat first or create .env from .env.template
    pause
    exit /b 1
)

echo Starting bot...
python Bot.py

if %errorlevel% neq 0 (
    echo.
    echo Bot stopped with error. Check the logs above.
    pause
)
