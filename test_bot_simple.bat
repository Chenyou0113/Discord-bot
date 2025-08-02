@echo off
cd /d "%~dp0"

echo Testing Discord Bot Configuration...
echo.

REM Test with virtual environment Python
if exist "venv\Scripts\python.exe" (
    echo Using virtual environment Python...
    "venv\Scripts\python.exe" test_bot_config.py
) else (
    echo Using system Python...
    python test_bot_config.py
)

echo.
pause
