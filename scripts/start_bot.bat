@echo off
chcp 65001 >nul
cd /d "%~dp0.."

echo Starting Discord Bot...
echo ==============================

if exist "venv\Scripts\python.exe" (
    echo Using virtual environment Python...
    "venv\Scripts\python.exe" bot.py
) else (
    echo Virtual environment not found! Using system Python...
    python bot.py
)

echo.
echo Bot has stopped. Press any key to exit...
pause >nul
