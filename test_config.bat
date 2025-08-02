@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Discord Bot Configuration Test
echo ================================

echo Checking Python environment...
if exist "venv\Scripts\python.exe" (
    echo [OK] Virtual environment Python found
    "venv\Scripts\python.exe" --version
) else (
    echo [ERROR] Virtual environment not found
)

echo.
echo Checking configuration files...
if exist "bot.py" (
    echo [OK] bot.py found
) else (
    echo [ERROR] bot.py not found
)

if exist ".env" (
    echo [OK] .env file found
) else (
    echo [ERROR] .env file not found
)

if exist "requirements.txt" (
    echo [OK] requirements.txt found
) else (
    echo [ERROR] requirements.txt not found
)

echo.
echo Running quick configuration test...
"venv\Scripts\python.exe" test_bot_config.py

echo.
echo Test completed. Press any key to exit...
pause >nul
