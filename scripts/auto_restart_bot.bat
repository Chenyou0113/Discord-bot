@echo off
chcp 65001 >nul
title Discord Bot - 自動重啟監控

echo 🤖 Discord Bot 自動重啟監控腳本
echo ====================================
echo.
echo 此腳本將監控機器人運行狀態，並在機器人關閉時自動重啟
echo 按 Ctrl+C 可停止監控並退出
echo.

REM 切換到專案根目錄
cd /d "%~dp0.."

REM 檢查必要檔案
if not exist "bot.py" (
    echo ❌ 錯誤: 找不到 bot.py
    pause
    exit /b 1
)

REM 啟用虛擬環境 (如果存在)
if exist "venv\Scripts\activate.bat" (
    echo 🔧 啟用虛擬環境...
    call venv\Scripts\activate.bat
    echo ✅ 虛擬環境已啟用
    echo.
)

:restart_loop
echo.
echo 🚀 正在啟動 Discord Bot...
echo 📅 啟動時間: %date% %time%
echo ================================
echo.

REM 啟動機器人
python bot.py

REM 檢查退出代碼
if %ERRORLEVEL% EQU 0 (
    echo.
    echo 🔄 機器人正常關閉，準備重啟...
    echo ⏳ 等待 3 秒後重新啟動...
    timeout /t 3 /nobreak >nul
    goto restart_loop
) else (
    echo.
    echo ❌ 機器人異常退出 (錯誤代碼: %ERRORLEVEL%)
    echo.
    echo 可能的原因:
    echo - Discord Token 無效
    echo - 網路連線問題
    echo - 程式碼錯誤
    echo.
    echo 是否要重試? (Y/N)
    choice /c YN /n /m "請選擇 [Y]是 [N]否: "
    if %ERRORLEVEL% EQU 1 (
        echo.
        echo 🔄 準備重新啟動...
        timeout /t 2 /nobreak >nul
        goto restart_loop
    ) else (
        echo.
        echo 🛑 停止自動重啟監控
        pause
        exit /b 1
    )
)
