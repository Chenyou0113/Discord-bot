@echo off
chcp 65001 >nul
echo 🤖 重啟 Discord Bot (自動搜尋功能)
echo ===================================
echo.

REM 切換到正確的目錄
cd /d "%~dp0"
echo 📁 目前目錄: %CD%
echo.

REM 檢查 bot.py 是否存在
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

echo 🚀 啟動 Discord Bot...
echo.
echo 💡 啟動後請在 Discord 使用: /auto_search enable:True
echo 💡 按 Ctrl+C 可停止 Bot
echo.

REM 啟動 Bot
python bot.py

echo.
echo 🛑 Bot 已停止
pause
