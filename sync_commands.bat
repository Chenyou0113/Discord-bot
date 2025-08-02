@echo off
cd /d "%~dp0"

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
