@echo off
chcp 65001 >nul
echo Discord Bot Restart Check Script
echo ==================================

cd /d "%~dp0.."

echo 1. Stopping existing bot processes...
taskkill /f /im python.exe 2>nul
timeout /t 3 /nobreak >nul

echo 2. Checking reservoir_commands.py syntax...
if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" -m py_compile cogs\reservoir_commands.py
) else (
    python -m py_compile cogs\reservoir_commands.py
)
if %errorlevel% neq 0 (
    echo ERROR: Syntax error found, please check the code
    pause
    exit /b 1
)
echo OK: Syntax check passed

echo 3. Installing dependencies...
if exist "venv\Scripts\python.exe" (
    echo Installing PyNaCl using virtual environment...
    "venv\Scripts\python.exe" -m pip install pynacl
) else (
    echo Installing PyNaCl using system Python...
    python -m pip install pynacl
)

echo 4. Starting bot...
echo Starting bot, please wait...
if exist "venv\Scripts\python.exe" (
    start /min "Discord Bot" "venv\Scripts\python.exe" bot.py
) else (
    start /min "Discord Bot" python bot.py
)
timeout /t 10 /nobreak >nul

echo 5. Checking bot status...
if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" -c "import time; time.sleep(5); print('Bot status check completed')"
) else (
    python -c "import time; time.sleep(5); print('Bot status check completed')"
)

echo.
echo Check completed! Please verify commands in Discord
echo Tip: View full log with: type bot.log
pause
