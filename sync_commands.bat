@echo off
cd /d "c:\Users\xiaoy\Desktop\Discord bot"

echo Syncing Discord Commands...
echo.

REM Sync commands with virtual environment Python
if exist "venv\Scripts\python.exe" (
    echo Using virtual environment Python...
    "venv\Scripts\python.exe" sync_commands.py
) else (
    echo Using system Python...
    python sync_commands.py
)

echo.
pause
