@echo off
chcp 65001 >nul
title Discord Bot Auto Restart Monitor

echo Discord Bot Auto Restart Monitor
echo ====================================
echo.
echo This script will monitor bot status and restart when it stops
echo Press Ctrl+C to stop monitoring and exit
echo.

REM Switch to project root directory
cd /d "%~dp0.."

REM Check required files
if not exist "bot.py" (
    echo ERROR: bot.py not found
    pause
    exit /b 1
)

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo Virtual environment activated
    echo.
)

:restart_loop
echo.
echo Starting Discord Bot...
echo Start time: %date% %time%
echo ================================
echo.

REM Start the bot
python bot.py

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Bot shutdown normally, preparing to restart...
    echo Waiting 3 seconds before restart...
    timeout /t 3 /nobreak >nul
    goto restart_loop
) else (
    echo.
    echo Bot exited with error code: %ERRORLEVEL%
    echo.
    echo Possible causes:
    echo - Invalid Discord Token
    echo - Network connection issues  
    echo - Code errors
    echo.
    echo Do you want to retry? Y/N
    choice /c YN /n /m "Choose [Y]es [N]o: "
    if %ERRORLEVEL% EQU 1 (
        echo.
        echo Preparing to restart...
        timeout /t 2 /nobreak >nul
        goto restart_loop
    ) else (
        echo.
        echo Stopping auto restart monitor
        pause
        exit /b 1
    )
)
