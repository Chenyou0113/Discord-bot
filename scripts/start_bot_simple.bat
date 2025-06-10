@echo off
chcp 65001 >nul
title Discord Bot 啟動器

REM 切換到腳本的上層目錄（專案根目錄）
cd /d "%~dp0.."

echo ========================================
echo          Discord Bot 啟動器
echo ========================================
echo.

REM 檢查 Python
echo [1/5] 檢查 Python...

REM 首先檢查虛擬環境
if exist "venv\Scripts\python.exe" (
    echo [信息] 找到虛擬環境，正在啟用...
    call "venv\Scripts\activate.bat"
    echo [成功] 虛擬環境已啟用
    set PYTHON_CMD=python
) else (
    echo [警告] 未找到虛擬環境，嘗試使用系統 Python...
    where python >nul 2>&1
    if errorlevel 1 (
        py --version >nul 2>&1
        if errorlevel 1 (
            echo [錯誤] 找不到 Python
            echo 請確認 Python 已安裝並加入系統 PATH
            pause
            exit /b 1
        ) else (
            set PYTHON_CMD=py
        )
    ) else (
        set PYTHON_CMD=python
    )
)

%PYTHON_CMD% --version
echo [成功] Python 檢查通過
echo.

REM 檢查主要文件
echo [2/5] 檢查主要文件...
if not exist "bot.py" (
    echo [錯誤] 找不到 bot.py
    pause
    exit /b 1
)
if not exist "cogs" (
    echo [錯誤] 找不到 cogs 目錄
    pause
    exit /b 1
)
echo [成功] 主要文件檢查通過
echo.

REM 檢查環境變數
echo [3/5] 檢查環境變數...
if not exist ".env" (
    echo [警告] 找不到 .env 文件
    echo 請確保已配置 DISCORD_TOKEN 和 GOOGLE_API_KEY
    echo.
) else (
    echo [成功] 找到 .env 文件
)

REM 測試套件導入
echo [4/5] 測試套件導入...
%PYTHON_CMD% -c "import discord, google.generativeai" 2>nul
if errorlevel 1 (
    echo [警告] 某些套件可能未正確安裝
    echo 嘗試執行: %PYTHON_CMD% -m pip install -r requirements.txt
) else (
    echo [成功] 主要套件檢查通過
)
echo.

echo ========================================
echo            啟動機器人
echo ========================================
echo [啟動] 正在啟動 Discord 機器人...
echo [提示] 按 Ctrl+C 可停止機器人
echo.

%PYTHON_CMD% bot.py

echo.
echo ========================================
echo            機器人已停止
echo ========================================
pause
