@echo off
chcp 65001 >nul
echo 🤖 Discord Bot 安全重啟腳本
echo ================================
echo.

REM 切換到正確的目錄
cd /d "%~dp0"
echo 📁 工作目錄: %CD%
echo.

REM 檢查是否有虛擬環境
if exist "venv\Scripts\activate.bat" (
    echo 🔧 啟用虛擬環境...
    call venv\Scripts\activate.bat
    echo ✅ 虛擬環境已啟用
) else (
    echo ⚠️  未找到虛擬環境，使用系統 Python
)
echo.

REM 檢查 bot.py 是否存在
if not exist "bot.py" (
    echo ❌ 錯誤: 找不到 bot.py 文件
    echo 📁 請確認您在正確的目錄中
    pause
    exit /b 1
)

REM 溫和地嘗試停止現有的 Bot (如果正在運行)
echo 🛑 檢查並停止現有的 Bot 進程...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| find "python.exe"') do (
    echo 發現 Python 進程，等待自然結束...
    timeout /t 3 /nobreak >nul
)

REM 啟動 Bot
echo.
echo 🚀 啟動 Discord Bot (含自動搜尋功能)...
echo ================================================
echo.
echo 如要停止 Bot，請按 Ctrl+C
echo.

REM 啟動 Bot 並保持在前台
python bot.py

REM 如果 Bot 意外停止
echo.
echo ⚠️  Bot 已停止運行
echo.
echo 可能的原因:
echo - Token 無效或過期
echo - 網路連線問題  
echo - 程式碼錯誤
echo - 手動停止
echo.
pause
