@echo off
chcp 65001 >nul
cd /d "c:\Users\xiaoy\Desktop\Discord bot"

echo Discord Bot Quick Status Check
echo =================================

echo [1/4] Checking virtual environment...
if exist "venv\Scripts\python.exe" (
    echo [OK] Virtual environment found
) else (
    echo [ERROR] Virtual environment not found
    goto :end
)

echo.
echo [2/4] Checking configuration...
if exist ".env" (
    echo [OK] Configuration file found
) else (
    echo [ERROR] .env file missing
    goto :end
)

echo.
echo [3/4] Checking main bot file...
if exist "bot.py" (
    echo [OK] Main bot file found
) else (
    echo [ERROR] bot.py missing
    goto :end
)

echo.
echo [4/4] Quick module check...
"venv\Scripts\python.exe" -c "import discord, aiohttp, google.generativeai; print('[OK] Core modules available')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Missing required modules
    goto :end
)

echo.
echo ================================
echo [SUCCESS] Bot is ready to start!
echo ================================
echo.
echo Available commands:
echo - start_bot_simple.bat   : Start the bot
echo - test_all_functions.py  : Run full tests
echo - sync_commands.bat      : Sync Discord commands
echo.

:end
echo Press any key to exit...
pause >nul
