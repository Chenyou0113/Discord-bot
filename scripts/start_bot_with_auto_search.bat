@echo off
chcp 65001 >nul
title Discord Bot - 自動搜尋功能
echo.
echo 🤖 啟動 Discord Bot (含自動搜尋功能)
echo =====================================
echo.

REM 切換到腳本的上層目錄（專案根目錄）
cd /d "%~dp0.."

REM 檢查必要文件
if not exist "bot.py" (
    echo ❌ 錯誤: 找不到 bot.py 文件
    echo 請確認您在正確的目錄中執行此腳本
    echo.
    pause
    exit /b 1
)

if not exist ".env" (
    echo ⚠️  警告: 找不到 .env 文件
    echo Bot 可能無法正常運行
    echo.
)

REM 啟用虛擬環境 (如果存在)
if exist "venv\Scripts\activate.bat" (
    echo 🔧 啟用虛擬環境...
    call venv\Scripts\activate.bat
    echo ✅ 虛擬環境已啟用
) else (
    echo ⚠️  使用系統 Python (建議使用虛擬環境)
)
echo.

REM 顯示使用說明
echo 📋 自動搜尋功能使用說明:
echo ----------------------------------------
echo 1. Bot 啟動後，在 Discord 中使用管理員帳號
echo 2. 輸入指令: /auto_search enable:True
echo 3. 用戶可以在對話中使用: "搜尋 [關鍵字]"
echo 4. Bot 會自動檢測並執行搜尋
echo.
echo 💡 控制提示:
echo - 按 Ctrl+C 可安全停止 Bot
echo - 如需重新啟動，請關閉此視窗後重新執行腳本
echo.

echo 🚀 正在啟動 Discord Bot...
echo ========================================
echo.

REM 啟動 Bot
python bot.py

REM Bot 停止後的處理
echo.
echo 🛑 Discord Bot 已停止運行
echo.
echo 如果這是意外停止，請檢查:
echo - Discord Token 是否有效
echo - 網路連線是否正常
echo - 控制台是否有錯誤訊息
echo.
pause
