@echo off
chcp 65001 >nul
title Discord Bot 自動重啟啟動器

echo ============================================================
echo Discord Bot 自動重啟啟動器
echo ============================================================

REM 切換到專案根目錄
cd /d "%~dp0.."

REM 檢查虛擬環境 Python
if exist "venv\Scripts\python.exe" (
    echo ✅ 找到虛擬環境 Python
    set PYTHON_CMD=venv\Scripts\python.exe
) else (
    REM 檢查系統 Python
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Python 未安裝或未加入 PATH
        echo 請安裝 Python 3.8+ 並確保已加入系統 PATH
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
)

for /f "tokens=*" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python 版本: %PYTHON_VERSION%

REM 檢查必要文件
if not exist "bot.py" (
    echo ❌ 找不到 bot.py
    pause
    exit /b 1
)

if not exist "bot_restarter.py" (
    echo ❌ 找不到 bot_restarter.py
    pause
    exit /b 1
)

if not exist ".env" (
    echo ❌ 找不到 .env 文件
    echo 請確保 .env 文件存在並包含必要的 API 金鑰
    pause
    exit /b 1
)

echo ✅ 所有必要文件已找到

REM 檢查依賴套件
echo.
echo 🔍 檢查依賴套件...
python -c "import discord; import aiohttp; import google.generativeai; print('✅ 所有依賴套件已安裝')" 2>nul
if errorlevel 1 (
    echo ❌ 部分依賴套件未安裝
    echo 正在安裝依賴套件...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依賴套件安裝失敗
        pause
        exit /b 1
    )
)

echo.
echo 🚀 啟動自動重啟監控器...
echo 💡 使用 /restart 指令可以重啟機器人
echo 💡 按 Ctrl+C 可以停止監控器
echo.

REM 啟動自動重啟監控器
python bot_restarter.py

echo.
echo 📋 監控器已關閉
pause