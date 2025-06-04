REM 最新版本的 Discord 機器人啟動腳本
@echo off
chcp 65001 >nul
title Discord Bot - 2025版本

echo ================================================
echo        Discord Bot 啟動腳本 (2025年版本)
echo ================================================
echo.
echo 此腳本將啟動並監控 Discord 機器人
echo 功能：
echo   - 支持2025年地震資料新格式
echo   - 優化的互動界面
echo   - 改進的天氣顯示
echo   - 等級系統性能優化
echo.

REM 檢查 Python 環境
echo [1/5] 檢查 Python 環境...

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
            goto :error
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

REM 檢查主要檔案
echo [2/5] 檢查主要檔案...
if not exist "bot.py" (
    echo [錯誤] 找不到主程式檔案 bot.py
    pause
    goto :error
)

if not exist "cogs" (
    echo [錯誤] 找不到 cogs 目錄
    pause
    goto :error
)

if not exist "cogs\info_commands_fixed_v4_clean.py" (
    echo [警告] 找不到資訊指令模組
)

if not exist "cogs\level_system.py" (
    echo [警告] 找不到等級系統模組
)

echo [成功] 主要檔案檢查通過
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

REM 檢查環境變數配置
%PYTHON_CMD% -c "import os; from dotenv import load_dotenv; load_dotenv(); print('[成功] 環境變數載入完成' if os.getenv('DISCORD_TOKEN') and os.getenv('GOOGLE_API_KEY') else '[警告] 請檢查 .env 文件中的 TOKEN 配置')" 2>nul
echo.

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

echo ================================================
echo            啟動機器人 [5/5]
echo ================================================
echo [啟動] 正在啟動 Discord 機器人...
echo [提示] 按 Ctrl+C 可停止機器人
echo.

%PYTHON_CMD% bot.py

echo.
echo ================================================
echo            機器人已停止
echo ================================================

goto :end

:error
echo.
echo ================================================
echo                    發生錯誤
echo ================================================
echo 請檢查上方錯誤信息，或查閱 bot.log 檔案以獲取更多資訊。
pause
exit /b 1

:end
echo.
echo ================================================
echo              機器人已正常關閉
echo ================================================
pause
exit /b 0
